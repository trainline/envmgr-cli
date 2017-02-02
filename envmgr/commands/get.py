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
        elif self.cmds['slice']:
            self.get_service_slice(**self.cli_args)
    

    def get_overall_health(self, service, env):
        result = self.api.get_service_overall_health(service, env)
        for asg in result['AutoScalingGroups']:
            service = asg['Services'][0]
            self.show_health(service)
        

    def get_service_health(self, service, slice, env):        
        result = self.api.get_service_health(service, env, slice)
        self.show_health(result)


    def get_service_slice(self, service, env):
        active = "true" if self.cmds['active'] else "false"
        result = self.api.get_service_slices(service, env, active)
        for slice in result:
            self.show_slice(slice)


    def show_health(self, service):
        slice = service['Slice']
        status = service['OverallHealth']
        n_healthy = service['InstancesCount']['Healthy']
        n_total = service['InstancesCount']['Total']
        print("{0} is {1} ({2} of {3} instances Healthy)".format(slice, status, n_healthy, n_total))


    def show_slice(self, slice):
        name = slice['Name']
        status = slice['State']
        upstream = slice['UpstreamName']
        print("{0} is {1} ({2})".format(name, status, upstream))
