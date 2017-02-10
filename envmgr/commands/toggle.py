""" Toggle Service Commands """

from envmgr.commands.base import BaseCommand

class Toggle(BaseCommand):

    def run(self):
        self.toggle_service_slices(**self.cli_args)


    def toggle_service_slices(self, service, env):
        result = self.api.put_service_slices_toggle(service, env)
        self.show_result(result, "{0} was toggled in {1}".format(service, env))

