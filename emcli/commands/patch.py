# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import semver
import time
import sys
import os

from envmgr import EmClient, ASG

from emcli.commands.base import BaseCommand
from emcli.commands.patching.patch_operation import PatchOperation
from emcli.commands.patching.patch_table import patch_table
from emcli.commands.patching.validate import server_has_valid_ami
from emcli.commands.user_confirmation import confirm
from math import ceil
from repoze.lru import lru_cache

class PatchCommand(BaseCommand):
    amis = []
    servers = []
    all_servers = []

    def __init__(self, options, *args, **kwargs):
        super(PatchCommand, self).__init__(options, *args, **kwargs)
        self.api = EmClient()
        self._register(('get', 'status'), self.describe_status)
        self._register(('patch', '!get'), self.run_patch_update)

    def describe_status(self, cluster, env):
        if PatchOperation.is_in_progress(cluster, env):
            self.show_current_status(cluster, env)
        else:
            self.get_patch_status(cluster, env)
    
    def show_current_status(self, cluster, env):
        patch_operation = PatchOperation.get_current(cluster, env)
        patch_status = PatchOperation.get_current_status(cluster, env)
        self.stop_spinner()
        self.show_result(patch_operation, patch_status)

    def get_patch_status(self, cluster, env):
        from_ami = self.opts.get('from-ami')
        to_ami = self.opts.get('to-ami')
        whitelist = self.get_user_filter('whitelist', 'match')
        blacklist = self.get_user_filter('blacklist', 'ignore')
        result = self.get_patch_requirements(cluster, env, from_ami, to_ami, whitelist, blacklist)

        if not result:
            self.patch_not_required(cluster, env)
        else:
            message = PatchOperation.describe_patches(result)
            self.show_result(result, message)

    def get_user_filter(self, filename, argname):
        argvalue = self.opts.get(argname)
        filter_file = self.opts.get(filename)
        if len(argvalue):
            return argvalue
        elif filter_file is not None:
            filepath = os.path.abspath(filter_file)
            with open(filepath) as f:
                filter_list = f.readlines()
            return [x.strip() for x in filter_list]

    def patch_not_required(self, cluster, env):
        self.show_result({}, '{0} do not need to patch any Windows servers in {1}'.format(cluster, env))

    def run_patch_update(self, cluster, env):
        env = env.lower()
        if self.environment_is_protected(env):
            self.stop_spinner()
            print('Bulk patching is temporarily disabled in {0}'.format(env))
            return

        if self.opts.get('kill', False):
            self.stop_spinner()
            PatchOperation.kill(cluster, env)
        else:
            patch_operation = PatchOperation(self.api)
            current_operation = PatchOperation.get_current(cluster, env)
            
            if current_operation is None:
                from_ami = self.opts.get('from-ami')
                to_ami = self.opts.get('to-ami')
                whitelist = self.get_user_filter('whitelist', 'match')
                blacklist = self.get_user_filter('blacklist', 'ignore')
                current_operation = self.get_patch_requirements(cluster, env, from_ami, to_ami, whitelist, blacklist)
                self.stop_spinner()
                if not current_operation:
                    return self.patch_not_required(cluster, env)
                if not self.confirm_patch(current_operation):
                    return
                else:
                    print('')
            
            patch_operation.run(current_operation, cluster, env)

    def confirm_patch(self, patches):
        to_patch = PatchOperation.get_patches_by_availability(patches, True)
        to_ignore = PatchOperation.get_patches_by_availability(patches, False)
        to_ignore += [ {'server_name':server, 'invalid_ami':True} for server in self.ignored_servers ]
        message = PatchOperation.describe_patches(to_patch, to_ignore)
        if not to_patch:
            self.show_result({}, message)
            return False
        else:
            if self.opts.get('ci-mode'):
                return True
            else:
                message.append('Do you want to continue? (y/n) ')
                return confirm(message)

    def get_patch_requirements(self, cluster, env, from_ami=None, to_ami=None, whitelist=None, blacklist=None):
        # We're only interested in Windows as Linux instances auto-update
        self.amis = self.api.get_images()
        self.amis = [ ami for ami in self.amis if ami.get('Platform') == 'Windows' ]
        self.validate_ami_compatibility(from_ami, to_ami)
        
        # List of clusters' servers with AMI info
        self.servers = self.api.get_environment_servers(env).get('Value')
        self.servers = [ server for server in self.servers if 
            'Ami' in server and server.get('Cluster').lower() == cluster.lower() 
            and server.get('IsBeingDeleted') != True
        ]
        
        # Filter out odd servers with no valid AMI info
        self.ignored_servers = [ server.get('Name') for server in self.servers if not server_has_valid_ami(server) ]
        self.servers = [ server for server in self.servers if server_has_valid_ami(server) ]

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
        self.get_asg_details(patches, env)
        return patches

    def environment_is_protected(self, env):
        result = self.api.get_environment_protected(env, 'BULK_PATCH_AMI')
        return result.get('isProtected', False)

    def get_asg_details(self, patches, env):
        for p in patches:
            asg_name = p.get('server_name')
            asg = self.api.get_asg(env, asg_name)
            # Calculate required scale out size
            n_azs = len(list(asg.get('AvailabilityZones')))
            n_instances = p.get('instances_count')
            scale_up_count = n_instances * 2
            if scale_up_count >= n_azs and scale_up_count % n_azs != 0:
                scale_up_count += 1
            p['az_count'] = n_azs
            p['scale_up_count'] = scale_up_count
            p['max_count'] = asg.get('MaxSize', n_instances)

            # Check for any instances in standby
            if any([ instance for instance in asg.get('Instances', []) if instance.get('LifecycleState') == 'Standby' ]):
                p['has_standby_instances'] = True
            # Check for overall health
            asg_status = ASG(asg_name, env).get_health()
            if not asg_status.get('is_healthy'):
                p['unhealthy'] = asg_status

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
        target_version = target.get('AmiVersion')
        patch = {
            'server_name': server.get('Name'),
            'current_version': from_version,
            'target_version': target_version,
            'ami_type': target.get('AmiType'),
            'new_ami_id': target.get('ImageId'),
            'server_role': server.get('Role'),
            'services_count': len(list(server.get('Services'))),
            'instances_count': server.get('Size').get('Current')
        }
        # Warn if target version is older than current verion
        if semver.compare(target_version, from_version) != 1:
            patch['Warning'] = True

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

