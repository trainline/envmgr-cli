# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr import EmClient
from emcli.commands.base import BaseCommand

class VerifyCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(VerifyCommand, self).__init__(options, *args, **kwargs)
        self._register('verify', self.verify_setup)

    def verify_setup(self):
        client = EmClient()
        result = client.get_accounts_config()
        if result is not None:
            msg = 'Hooray, envmgr cli is correctly configured.'
        else:
            msg = 'Verify failed, see error for log for details'
        self.show_result({}, msg)

