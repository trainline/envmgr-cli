# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import semver

from envmgr.commands.base import BaseCommand
from envmgr.commands.patch_state import PatchState
from math import ceil
from tabulate import tabulate
from repoze.lru import lru_cache

class Patch(BaseCommand):
    amis = []
    servers = []
    state = None

    def run(self):
        if self.cmds.get('get') and self.cmds.get('status'):
            self.get_patch_status(**self.cli_args)
        else:
            self.run_patch_update(**self.cli_args)
    
    def get_patch_status(self, cluster, env):
        from_ami = self.opts.get('from-ami')
        to_ami = self.opts.get('to-ami')
        result = self.get_patch_requirements(cluster, env, from_ami, to_ami)

        if not result:
            self.show_result(result, 'All {0} Windows servers are up to date in {1}'.format(cluster, env))
        else:
            messages = ['The following patch operations are required:']
            table_data = map(lambda p: {
                0: p.get('server_name'),
                1: p.get('instances_count'),
                2: p.get('from_ami'),
                3: '->',
                4: p.get('scale_up_count'),
                5: p.get('to_ami'),
                6: 'WARNING' if p.get('Warning') is not None else ''
                }, result)
            messages.append(tabulate(table_data, tablefmt="plain"))
            self.show_result(result, messages)

    def run_patch_update(self, cluster, env):
        pass
        """
        self.state = PatchState(self.api)
        patch = self.state.get_patch_if_exists(cluster, env)
        
        if patch is None:
            self.scale_out()
        else:
            state = patch.get('state')
            if state == self.WAIT_FOR_SCALE_OUT:
                self.wait_for_scale_out()
            elif state == self.WAIT_FOR_SCALE_IN:
                self.wait_for_scale_in()
            else:
                print('Unknown state')
        """

    def get_patch_requirements(self, cluster, env, from_ami=None, to_ami=None):
        # We're only interested in Windows as Linux instances auto-update
        self.amis = self.api.get_images()
        self.amis = [ ami for ami in self.amis if ami.get('Platform') == 'Windows' ]
        self.validate_ami_compatibility(from_ami, to_ami)
        
        # List of clusters' servers with AMI info
        self.servers = self.api.get_environment_servers(env).get('Value')
        self.servers = [ server for server in self.servers if 
            'Ami' in server and server.get('Cluster').lower() == cluster.lower() ]
        
        # Update any non-latest-stable if no "from ami" given
        if from_ami is not None: 
            is_out_of_date = lambda ami,server: ami.get('Name') == from_ami
        else:
            is_out_of_date = lambda ami,server: not ami.get('IsLatestStable')
        
        # List of requirements to be considered for updates
        # Prefer 'latest stable' info from image, not server
        update_requirements = [
            lambda ami,server: ami.get('Name') == server.get('Ami').get('Name'),
            is_out_of_date
        ]
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
        target = self.get_target_ami(from_name)
        to_name = target.get('Name')
        from_version = from_ami.get('AmiVersion')
        to_version = target.get('AmiVersion')
        patch = {
            'server_name': server.get('Name'),
            'from_ami': from_name,
            'to_ami': to_name,
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
        if from_ami is not None and to_ami is not None:
            if from_ami['AmiType'] != to_ami['AmiType']:
                raise ValueError('AMI types for from_ami and to_ami must match')

