# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr.commands.base import BaseCommand
from tabulate import tabulate

class Patch(BaseCommand):
    amis = []
    servers = []

    def run(self):
        self.get_patch_status(**self.cli_args)
    
    def get_patch_status(self, cluster, env):
        from_ami = self.opts.get('from-ami')
        to_ami = self.opts.get('to-ami')
        result = self.get_patch_requirements(cluster, env, from_ami, to_ami)

        if not result:
            self.show_result(result, 'All {0} Windows servers are up to date in {1}'.format(cluster, env))
        else:
            messages = ['The following patch operations are required:']
            table_data = map(lambda p: {
                0: p['server_name'],
                1: p['instances_count'],
                2: p['from_ami'],
                3: '->',
                4: p['to_ami']
                }, result)
            messages.append(tabulate(table_data, tablefmt="plain"))
            self.show_result(result, messages)


    def get_patch_requirements(self, cluster, env, from_ami=None, to_ami=None):
        # We're only interested in Windows as Linux instances auto-update
        self.amis = self.api.get_images()
        self.amis = [ ami for ami in self.amis if ami['Platform'] == 'Windows' ]
        self.validate_ami_compatibility(from_ami, to_ami)
        
        # List of clusters' servers with AMI info
        self.servers = self.api.get_environment_servers(env)['Value']
        self.servers = [ server for server in self.servers if 
            'Ami' in server and server['Cluster'].lower() == cluster.lower() ]
        
        # Update any non-latest-stable if no "from ami" given
        if from_ami is not None: 
            is_out_of_date = lambda ami,server: ami['Name'] == from_ami
        else:
            is_out_of_date = lambda ami,server: not ami['IsLatestStable']
        
        # List of requirements to be considered for updates
        # Prefer 'latest stable' info from image, not server
        update_requirements = [
            lambda ami,server: ami['Name'] == server['Ami']['Name'],
            is_out_of_date
        ]
        # List of servers with Windows AMI that matches update requirement
        servers_to_update = [ server for server in self.servers if 
            any(ami for ami in self.amis if 
                all([ requirement(ami,server) for requirement in update_requirements ])
            )
        ]
        # List of patches to apply
        return map(self.create_patch_item, servers_to_update)

    def create_patch_item(self, server):
        from_name = server['Ami']['Name']
        target = self.get_target_ami(from_name)
        to_name = target['Name']
        patch = {
            'server_name': server['Name'],
            'from_ami': from_name,
            'to_ami': to_name,
            'server_role': server['Role'],
            'services_count': len(server['Services']),
            'instances_count': server['Size']['Current']
        }
        return patch

    def get_target_ami(self, from_name):
        from_ami = self.get_ami_by_key('Name', from_name)
        ami_type = from_ami['AmiType']
        ami = [ ami for ami in self.amis if ami['AmiType'] == ami_type and ami['IsLatestStable'] == True]
        return ami[0]

    def get_ami_by_key(self, key, value, unique=True):
        ami = [ ami for ami in self.amis if ami[key] == value ]
        if not ami:
            raise ValueError('Could not find AMI with {0}={1}'.format(key, value))
        elif unique and len(ami) != 1:
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

