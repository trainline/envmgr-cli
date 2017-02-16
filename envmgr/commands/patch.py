# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr.commands.base import BaseCommand
from tabulate import tabulate

class Patch(BaseCommand):

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
        servers = self.api.get_environment_servers(env)['Value']
        all_amis = self.api.get_images()
        
        # We're only interested in Windows as Linux instances auto-update
        windows_amis = [ ami for ami in all_amis if ami['Platform'] == 'Windows' ]

        # Validate AMI specs
        self.validate_ami_compatibility(windows_amis, from_ami, to_ami)

        # List of clusters' servers with AMI info
        servers = [ server for server in servers if 
            'Ami' in server and server['Cluster'].lower() == cluster.lower() ]
        
        # Update any non-latest-stable if no "from ami" given
        if from_ami is not None: 
            is_out_of_date = lambda ami,server: ami['Name'] == from_ami
        else:
            is_out_of_date = lambda ami,server: not ami['IsLatestStable']

        # List of requirements to be considered for updates
        matchers = [
            lambda ami,server: ami['Name'] == server['Ami']['Name'],
            is_out_of_date
        ]
        
        # List of matching servers
        servers_to_update = [ server for server in servers if 
            any(ami for ami in windows_amis if 
                all([ match(ami,server) for match in matchers ])
            )
        ]

        def patch_transform(s):
            from_name = s['Ami']['Name']
            target = self.get_target_ami(windows_amis, from_name)
            to_name = target['Name']
            return {
                'server_name':s['Name'],
                'from_ami':from_name,
                'to_ami':to_name,
                'server_role':s['Role'],
                'services_count':len(s['Services']),
                'instances_count':s['Size']['Current']
            }

        patches = map(patch_transform, servers_to_update)
        return patches

    def get_target_ami(self, amis, from_name):
        from_ami = self.get_ami_by_key(amis, 'Name', from_name)
        ami_type = from_ami['AmiType']
        
        ami = [ ami for ami in amis if ami['AmiType'] == ami_type and ami['IsLatestStable'] == True]
        return ami[0]

    def get_ami_by_key(self, amis, key, value, unique=True):
        ami = [ ami for ami in amis if ami[key] == value ]
        if not ami:
            raise ValueError('Could not find AMI with {0}={1}'.format(key, value))
        elif unique and len(ami) != 1:
            raise ValueError('Multiple AMI definitions found with {0}={1}'.format(key, value))
        return ami[0]

    def validate_ami_compatibility(self, amis, from_name=None, to_name=None):
        from_ami = None
        to_ami = None

        if from_name is not None:
            from_ami = self.get_ami_by_key(amis, 'Name', from_name)

        if to_name is not None:
            to_ami = self.get_ami_by_key(amis, 'Name', to_name)

        if from_ami is not None and to_ami is not None:
            if from_ami['AmiType'] != to_ami['AmiType']:
                raise ValueError('AMI types for from_ami and to_ami must match')

