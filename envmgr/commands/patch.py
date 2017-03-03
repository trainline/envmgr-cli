# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import semver
import time
import sys
import os
import atexit

from envmgr.commands.base import BaseCommand
from envmgr.commands.patching.patch_operation import PatchOperation
from envmgr.commands.patching.patch_table import patch_table
from math import ceil
from repoze.lru import lru_cache

class Patch(BaseCommand):
    amis = []
    servers = []

    def run(self):
        if self.cmds.get('get') and self.cmds.get('status'):
            if PatchOperation.is_in_progress(**self.cli_args):
                self.show_current_status(**self.cli_args)
            else:
                self.get_patch_status(**self.cli_args)
        else:
            self.run_patch_update(**self.cli_args)
    
    def show_current_status(self, cluster, env):
        patch_operation = PatchOperation.get_current(cluster, env)
        patch_status = PatchOperation.get_current_status(cluster, env)
        self.show_result(patch_operation, patch_status)

    def get_patch_status(self, cluster, env):
        from_ami = self.opts.get('from-ami')
        to_ami = self.opts.get('to-ami')
        whitelist = self.opts.get('whitelist')
        blacklist = self.opts.get('blacklist')
        result = self.get_patch_requirements(cluster, env, from_ami, to_ami, whitelist, blacklist)

        if not result:
            self.patch_not_required(cluster, env)
        else:
            get_status = lambda p: 'WARNING' if p.get('Warning') is not None else ''
            table_data = patch_table(result, get_status)
            messages = ['', 'The following patch operations are required:', table_data]
            self.show_result(result, messages)

    def patch_not_required(self, cluster, env):
        self.show_result({}, '{0} do not need to patch any Windows servers in {1}'.format(cluster, env))

    def run_patch_update(self, cluster, env):
        if env.lower() == 'pr1':
            print('Bulk patching is disabled in production')
            return

        if self.opts.get('kill', False):
            PatchOperation.kill(cluster, env)
        else:
            patch_operation = PatchOperation(self.api)
            current_operation = PatchOperation.get_current(cluster, env)
            
            if current_operation is None:
                from_ami = self.opts.get('from-ami')
                to_ami = self.opts.get('to-ami')
                current_operation = self.get_patch_requirements(cluster, env, from_ami, to_ami)
                if not current_operation:
                    return self.patch_not_required(cluster, env)
            
            patch_operation.run(current_operation, cluster, env)

    def get_patch_requirements(self, cluster, env, from_ami=None, to_ami=None, whitelist=None, blacklist=None):
        # We're only interested in Windows as Linux instances auto-update
        self.amis = self.api.get_images()
        self.amis = [ ami for ami in self.amis if ami.get('Platform') == 'Windows' ]
        self.validate_ami_compatibility(from_ami, to_ami)
        
        # List of clusters' servers with AMI info
        self.servers = self.api.get_environment_servers(env).get('Value')
        self.servers = [ server for server in self.servers if 
            'Ami' in server and server.get('Cluster').lower() == cluster.lower() 
            and server.get('IsBeingDeleted') != True ]
        
        # List of requirements to be considered for updates
        # Prefer 'latest stable' info from image, not server
        update_requirements = [ lambda ami,server: ami.get('Name') == server.get('Ami').get('Name') ]
        
        # Update any non-latest-stable if no "from ami" given
        if from_ami is not None: 
            update_requirements.append( lambda ami,server: ami.get('Name') == from_ami )
        else:
            update_requirements.append( lambda ami,server: not ami.get('IsLatestStable') )
        if whitelist:
            update_requirements.append( lambda ami,server: server.get('Name') in whitelist )
        elif blacklist:
            update_requirements.append( lambda ami,server: server.get('Name') not in blacklist )
 
        # List of servers with Windows AMI that matches update requirement
        servers_to_update = [ server for server in self.servers if 
            any(ami for ami in self.amis if 
                all([ requirement(ami,server) for requirement in update_requirements ])
            )
        ]
        # List of patches to apply
        patches = list(map(self.create_patch_item, servers_to_update))
        self.assign_scale_requirements(patches, env)
        return patches

    def assign_scale_requirements(self, patches, env):
        for p in patches:
            asg = self.api.get_asg(env, p.get('server_name'))
            n_azs = len(list(asg.get('AvailabilityZones')))
            n_instances = p.get('instances_count')
            scale_up_count = n_instances * 2
            if scale_up_count >= n_azs and scale_up_count % n_azs != 0:
                scale_up_count += 1
            p['az_count'] = n_azs
            p['scale_up_count'] = scale_up_count

    def create_patch_item(self, server):
        from_name = server.get('Ami').get('Name')
        from_ami = self.get_ami_by_key('Name', from_name)
        target_name = self.opts.get('to-ami')
        if target_name is not None:
            target = self.get_ami_by_key('Name', target_name)
        else:
            target = self.get_target_ami(from_name)
            target_name = target.get('Name')
        from_version = from_ami.get('AmiVersion')
        to_version = target.get('AmiVersion')
        patch = {
            'server_name': server.get('Name'),
            'current_version': from_version,
            'to_ami': target_name,
            'new_ami_id': target.get('ImageId'),
            'server_role': server.get('Role'),
            'services_count': len(list(server.get('Services'))),
            'instances_count': server.get('Size').get('Current')
        }

        # Warn if target version is older than current verion
        if semver.compare(to_version, from_version) != 1:
            patch['Warning'] = 'Target version ({0}) is older than current version ({1})'.format(to_version, from_version)

        return patch

    @lru_cache(128)
    def get_target_ami(self, from_name):
        from_ami = self.get_ami_by_key('Name', from_name)
        ami_type = from_ami['AmiType']
        ami = [ ami for ami in self.amis if ami['AmiType'] == ami_type and ami['IsLatestStable'] == True]
        return ami[0]

    @lru_cache(128)
    def get_ami_by_key(self, key, value, unique=True):
        ami = [ ami for ami in self.amis if ami[key] == value ]
        if not ami:
            raise ValueError('Could not find AMI with {0}={1}'.format(key, value))
        elif unique and len(list(ami)) != 1:
            raise ValueError('Multiple AMI definitions found with {0}={1}'.format(key, value))
        return ami[0]

    def validate_ami_compatibility(self, from_name=None, to_name=None):
        from_ami = None
        to_ami = None
        if from_name is not None:
            from_ami = self.get_ami_by_key('Name', from_name)
        if to_name is not None:
            to_ami = self.get_ami_by_key('Name', to_name)
            if from_name is None:
                raise ValueError('You must specify --from-ami if --to-ami is given')
        if from_ami is not None and to_ami is not None:
            if from_ami['AmiType'] != to_ami['AmiType']:
                raise ValueError('AMI types for from_ami and to_ami must match')

