"""Patch commands"""

import time

from envmgr.commands.base import BaseCommand

class Patch(BaseCommand):

    def run(self):
        self.get_patch_requirements(**self.cli_args)


    def get_patch_requirements(self, cluster, env):
        if env == "pr1" or env == "PR1":
            print("Yeah, let's not do that huh?")
            return

        from_ami = self.opts.get("from_ami")
        to_ami = self.opts.get("to_ami")
        
        servers = self.api.get_environment_servers(env)["Value"]
        all_amis = self.api.get_images()

        filters = [
                lambda server: "Ami" in server,
                lambda server: server['Cluster'].lower() == cluster.lower()
                ]

        # Select only servers with AMI info and that match the given cluster
        servers = [ server for server in servers if 
                all([ f(server) for f in filters ])
                ]
        
        # List of lamdas that must match to be considered for updating
        matchers = [
                lambda ami,server: ami['Name'] == server['Ami']['Name'], 
                lambda ami,server: ami["Platform"] == "Windows"
                ]
        
        # If "from AMI" is specified, add matching predicate
        if from_ami is not None: matchers.append(
                lambda ami, server: ami["Name"] == from_ami
                )

        # Select only servers with a Windows platform AMI
        windows_servers = [
                server
                for server in servers
                if any(ami for ami in all_amis if 
                    all([ match(ami,server) for match in matchers ])
                    )
                ]

        # Select only windows serverts that aren't latest stable
        windows_servers_to_update = [
                server
                for server in windows_servers
                if not server["Ami"]["IsLatestStable"]
                ]

        n_windows = len(windows_servers)
        n_to_update = len(windows_servers_to_update)
        pluralized = "server" if n_windows == 1 else "servers"
        
        print("{0} have {1} Windows {2} in {3}. {4} need patching".format(cluster, n_windows, pluralized, env, n_to_update))

