"""Get Accounts config."""

from json import dumps
from envmgr.commands.base import BaseCommand

class Accounts(BaseCommand):

    def run(self):
        
        stuff = self.api.get_accounts_config()
        print(stuff)


