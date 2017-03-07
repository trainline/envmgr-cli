# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time
import os 

from json import dumps
from envmgr.commands.base import BaseCommand

class Service(BaseCommand):

    def run(self):
        self.show_activity()
        if self.cmds.get('healthy'):
            self.wait_for_healthy_service(**self.cli_args)
        elif self.cmds.get('health'):
            if 'slice' in self.cli_args:
                self.get_service_health(**self.cli_args)
            else:
                self.get_overall_health(**self.cli_args)
        elif self.cmds.get('slice'):
            self.get_service_slice(**self.cli_args)

    def wait_for_healthy_service(self, service, env, slice=None):
        while True:
            healthy = self.get_service_health(service, slice, env)
            if healthy:
                return
            else:
                time.sleep(5)

    def get_overall_health(self, service, env):
        result = self.api.get_service_overall_health(service, env)
        services = [ asg.get('Services')[0] for asg in result.get('AutoScalingGroups') ]
        messages = [ self.format_health(service) for service in services ]
        self.show_result(result, messages)
        return all( service.get("OverallHealth") == "Healthy" for service in services )

    def get_service_health(self, service, slice, env):        
        result = self.api.get_service_health(service, env, slice)
        message = self.format_health(result)
        self.show_result(result, message)
        return result.get("OverallHealth") == "Healthy"

    def get_service_slice(self, service, env):
        active = "true" if self.cmds.get('active') else "false"
        result = self.api.get_service_slices(service, env, active)
        messages = [ self.format_slice(slice) for slice in result ]
        self.show_result(result, messages)

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

