# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time
import os 

from json import dumps
from envmgr import Service
from emcli.commands.base import BaseCommand

class ServiceCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(ServiceCommand, self).__init__(options, *args, **kwargs)
        self._register('wait-for', self.wait_for_healthy_service, False)
        self._register('health', self.get_service_health)
        self._register('slice', self.get_service_slice)

    def get_service_health(self, service, env, slice=None):
        svc = Service(service, env)
        result = svc.get_health(slice)

        if result is None:
            self.show_result({}, 'Could not get health status for {0}'.format(service))
            return False

        if slice is None:
            message = [ self.format_health(service) for service in result ]
            is_healthy = all( service.get("OverallHealth") == "Healthy" for service in result )
        else:
            message = self.format_health(result)
            is_healthy = result.get("OverallHealth") == "Healthy"
        self.show_result(result, message)
        return is_healthy

    def get_service_slice(self, service, env):
        svc = Service(service, env)
        active = self.cmds.get('active', False)
        result = svc.get_slices(active)
        messages = [ self.format_slice(slice) for slice in result ]
        self.show_result(result, messages)

    def wait_for_healthy_service(self, service, env, slice=None):
        while True:
            healthy = self.get_service_health(service, env, slice)
            if healthy:
                return
            else:
                time.sleep(5)
    
    def format_health(self, service):
        slice = service.get('Slice')
        status = service.get('OverallHealth')
        n_healthy = service.get('InstancesCount').get('Healthy')
        n_total = service.get('InstancesCount').get('Total')
        return "{0} is {1} ({2} of {3} instances Healthy)".format(slice, status, n_healthy, n_total)

    def format_slice(self, slice):
        name = slice.get('Name')
        status = slice.get('State')
        upstream = slice.get('UpstreamName')
        return "{0} is {1} ({2})".format(name, status, upstream)

