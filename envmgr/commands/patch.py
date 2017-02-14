"""Patch commands"""

import time

from envmgr.commands.base import BaseCommand

class Patch(BaseCommand):

    def run(self):
        self.get_patch_status(**self.cli_args)

    
    def get_patch_status(self, cluster, env):
        from_ami = self.opts.get("from-ami")
        to_ami = self.opts.get("to-ami")
        result = self.get_patch_requirements(cluster, env, from_ami, to_ami)

        n_windows = len(result)
        server_desc = from_ami if from_ami is not None else "Windows"
        pluralized = "server" if n_windows == 1 else "servers"
        self.show_result(result,
                "{0} need to patch {1} {2} {3} in {4}".format(cluster, n_windows, server_desc, pluralized, env))


    def get_patch_requirements(self, cluster, env, from_ami=None, to_ami=None):
        if env == "pr1" or env == "PR1":
            print("Yeah, let's not do that huh?")
            return

        cluster = cluster.lower()
        from_ami = self.opts.get("from-ami")
        to_ami = self.opts.get("to-ami")
        servers = self.api.get_environment_servers(env)["Value"]
        all_amis = self.api.get_images()
        
        # We're only interested in Windows as Linux instances auto-update
        windows_amis = [ ami for ami in all_amis if ami["Platform"] == "Windows" ]

        # List of clusters' servers with AMI info
        servers = [ server for server in servers if 
            "Ami" in server and server['Cluster'].lower() == cluster ]
        
        # Update any non-latest-stable if no "from ami" given
        if from_ami is not None: 
            is_out_of_date = lambda ami,server: ami["Name"] == from_ami
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

        return servers_to_update


