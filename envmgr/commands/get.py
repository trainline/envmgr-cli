"""Get Accounts config."""

from json import dumps
from envmgr.commands.base import BaseCommand

class GetService(BaseCommand):

    def run(self):
        if self.cmds['health']:
            if 'slice' in self.cli_args:
                self.get_service_health(**self.cli_args)
            else:
                self.get_overall_health(**self.cli_args)
        elif self.cmds['active']:
            self.get_active_slice(**self.cli_args)


    def get_overall_health(self, service, env):
        result = self.api.get_service_overall_health(service, env)
        
        for asg in result['AutoScalingGroups']:
            service = asg['Services'][0]
            self.print_health(service)
        

    def get_service_health(self, service, slice, env):
        result = self.api.get_service_health(service, env, slice)
        self.print_health(result)


    def get_active_slice(self, service, env):
        result = self.api.get_service_slices(service, env, "true")
        print(result)


    def print_health(self, service):
        slice = service['Slice']
        status = service['OverallHealth']
        n_healthy = service['InstancesCount']['Healthy']
        n_total = service['InstancesCount']['Total']
        print("{0} is {1} ({2} of {3} instances Healthy)".format(slice, status, n_healthy, n_total))
