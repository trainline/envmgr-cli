# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time

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
            n = len(result)
            if n == 0:
                message = "{0} is not expected here and is not running here".format(slice)
                is_healthy = False
            elif n > 1:
                message = "Expected one service but found {0}".format(n)
                is_healthy = False
            else:
                (is_healthy, message) = self.get_health_summary(env, service, slice, result[0])
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

    @staticmethod
    def get_health_summary(env, service, slice, summary):
        desired_count = summary.get('desiredCount')
        desired_and_healthy_count = summary.get('desiredAndHealthyCount')
        undesired_count = summary.get('undesiredCount')
        service_name = "the {0} slice of {1} in {2}".format(slice, service, env)
        is_healthy = desired_and_healthy_count >= desired_count and undesired_count <= 0
        messages = filter(lambda x: x != None, [
            "is healthy" if is_healthy else None,
            "may be routing requests to {0} unintended instance{1}".format(undesired_count, "s" if undesired_count > 1 else "") if undesired_count > 0 else None,
            "is not operating at capacity ({0}/{1} healthy)".format(desired_and_healthy_count, desired_count) if desired_and_healthy_count < desired_count else None
        ])
        return (is_healthy, "{0} {1}".format(service_name, " and ".join(messages)))
