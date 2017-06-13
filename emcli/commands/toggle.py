# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time

from envmgr import Upstream, Service
from emcli.commands.base import BaseCommand

class ToggleCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(ToggleCommand, self).__init__(options, *args, **kwargs)
        self._register('wait-for', self.wait_for_toggle, False)
        self._register('status', self.get_upstream_status)
        self._register(('!get', '!to'), self.toggle_service_slices)

    def get_upstream_status(self, slice, service, env):
        name = self.opts.get('upstream')
        upstream = Upstream(service, slice, env, name)
        status = upstream.get_status()
        desc = "{0} is configured {1}, {2} of {3} upstreams are active across {4} load balancers".format(
            slice, 
            status.slice_config,
            status.active_upstreams,
            status.total_upstreams,
            status.total_load_balancers
        )
        self.show_result(status.__dict__, desc)
        return status

    def toggle_service_slices(self, service, env):
        svc = Service(service, env)
        upstream = svc.toggle()
        self.show_result(upstream, "{0} is now configured active for {1} in {2}".format(upstream.slice, service, env))

    def wait_for_toggle(self, slice, service, env):
        while True:
            status = self.get_upstream_status(slice, service, env)
            if status.is_active:
                return
            else:
                time.sleep(5)

