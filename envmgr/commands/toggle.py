# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr.commands.base import BaseCommand

class Toggle(BaseCommand):

    def run(self):
        if self.cmds.get("wait-for"):
            self.wait_for_toggle(**self.cli_args)
        else:
            self.show_activity()
            self.toggle_service_slices(**self.cli_args)

    def wait_for_toggle(self, slice, service, env):
        
        env = env.lower()
        env_type_name = self.api.get_environment_config(env).get('Value').get('EnvironmentType')
        env_type = self.api.get_environmenttype_config(env_type_name)
        env_load_balancers = list(env_type.get('Value').get('LoadBalancers'))
        lb_upstreams = map(lambda lb: self.api.get_loadbalancer(lb), env_load_balancers)

        if not self.opts.get('upstream'):
            svc_slices = self.api.get_service_slices(service, env)
            svc_slices = [ s for s in svc_slices if s.get('Name').lower() == slice ]
            if len(svc_slices) > 1:
                print('You must provide an --upstream value when multiple upstreams are attached to a service')
                return
            else:
                upstream = svc_slices[0].get('UpstreamName')
        else:
            upstream = self.opts.get('upstream')

        print(upstream)

        # self.show_result(lb_upstreams, lb_upstreams)

        """
        all_upstreams = map(lambda u: u.get('Value'), self.api.get_upstreams_config())
        svc_upstream = [ upstream for upstream in all_upstreams if 
            upstream.get('EnvironmentName').lower() == env and
            upstream.get('ServiceName').lower() == service
        ]

        self.show_result(svc_upstream, svc_upstream)
        """


    def toggle_service_slices(self, service, env):
        result = self.api.put_service_slices_toggle(service, env)
        self.show_result(result, "{0} was toggled in {1}".format(service, env))

