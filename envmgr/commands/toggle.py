# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time

from envmgr.commands.base import BaseCommand

class Toggle(BaseCommand):

    def run(self):
        if self.cmds.get("wait-for"):
            self.wait_for_toggle(**self.cli_args)
        elif self.cmds.get("status"):
            self.show_activity()
            self.describe_upstream_status(**self.cli_args)
        else:
            self.show_activity()
            self.toggle_service_slices(**self.cli_args)

    def describe_upstream_status(self, slice, service, env):
        (upstream_name, load_balancers) = self.get_upstream_and_lbs(slice, service, env)
        status = self.get_upstream_status(upstream_name, load_balancers, service, env)
        (result, desc) = self.format_status(status, slice, load_balancers)
        self.show_result(result, desc)

    def format_status(self, status, slice, load_balancers):
        config = [ config for config in status['upstream_config'] if config['name'] == slice ][0]
        slice_active = config.get('active')
        slice_state = 'up' if slice_active else 'down'
        matching_upstreams = [ u for u in status['upstream_status'] if u['port'] == config['port'] ]
        toggled_upstreams = [ u for u in matching_upstreams if u['active'] is True ]
        n_total = len(matching_upstreams)
        n_ready = len(toggled_upstreams)
        n_lb = len(load_balancers)
        toggle_complete = slice_active and n_ready is n_total and n_ready is not 0
        result = {
            'active': toggle_complete,
            'slice':slice,
            'slice_config':slice_state,
            'active_upstreams':n_ready,
            'total_upstreams':n_total,
            'total_load_balancers': n_lb
        }
        
        state = 'on' if slice_active else 'off'
        desc = "{0} is configured {1}, {2} of {3} upstreams are active across {4} load balancers".format(slice, state, n_ready, n_total, n_lb)
        return (result, desc)

    def wait_for_toggle(self, slice, service, env):
        (upstream_name, load_balancers) = self.get_upstream_and_lbs(slice, service, env)

        while True:
            status = self.get_upstream_status(upstream_name, load_balancers, service, env)
            (result, desc) = self.format_status(status, slice, load_balancers)
            self.show_result(result, desc)
            if result['active']:
                return
            else:
                time.sleep(10)

    def get_upstream_and_lbs(self, slice, service, env):
        env = env.lower()
        slice = slice.lower()
        if not self.opts.get('upstream'):
            svc_slices = self.api.get_service_slices(service, env)
            svc_slices = [ s for s in svc_slices if s.get('Name').lower() == slice ]
            if len(svc_slices) > 1:
                raise Exception('You must provide an --upstream value when multiple upstreams are attached to a service')
                return
            else:
                upstream_name = svc_slices[0].get('UpstreamName')
        else:
            upstream_name = self.opts.get('upstream')
        env_type_name = self.api.get_environment_config(env).get('Value').get('EnvironmentType')
        env_type = self.api.get_environmenttype_config(env_type_name)
        load_balancers = list(env_type.get('Value').get('LoadBalancers'))
        return (upstream_name, load_balancers)
    
    def get_upstream_status(self, upstream_name, load_balancers, service, env):
        all_upstreams = reduce(lambda a,b: a + self.api.get_loadbalancer(b), load_balancers, [])
        lb_upstreams = [ upstream for upstream in all_upstreams if upstream.get('Name') == upstream_name ] 
        lb_upstreams = reduce(lambda a,b: a + b.get('Hosts'), lb_upstreams, [])
        lb_upstreams = map(self.host_status, lb_upstreams)
        lb_config = map(self.slice_status, self.api.get_upstream_slices(upstream_name, env))
        return {'upstream_status':lb_upstreams, 'upstream_config':lb_config}

    def get_active_state(self, state):
        state = state.lower()
        return True if state == 'up' or state == 'active' else False

    def host_status(self, host):
        return {
            'active': self.get_active_state(host.get('State')),
            'port': int(host.get('Server').split(':')[1])
        }
    
    def slice_status(self, slice):
        return {
            'port': slice.get('Port'),
            'name': slice.get('Name').lower(),
            'active': self.get_active_state(slice.get('State'))
        }

    def toggle_service_slices(self, service, env):
        result = self.api.put_service_slices_toggle(service, env)
        self.show_result(result, "{0} was toggled in {1}".format(service, env))

