"""Service commands"""

from envmgr.commands.base import BaseCommand

class Service(BaseCommand):

    def run(self):
        
        if self.cmds["get-slices"]:
            self.get_slices(**self.cli_args)


    def get_slices(self, env, name)

