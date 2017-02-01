"""Get Accounts config."""

from json import dumps
from envmgr.commands.base import BaseCommand

class GetService(BaseCommand):

    def run(self):
	self.get_service_health(**self.cli_args)

    def get_service_health(self, service, slice, env):
        print("Get health of {0} {1} in {2}".format(service, slice, env))
