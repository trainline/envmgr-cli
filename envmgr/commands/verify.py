# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
import requests
import math

from json import dumps
from envmgr.commands.base import BaseCommand

class Verify(BaseCommand):

    def run(self):
        self.show_activity()
        simple_call = self.api.get_accounts_config()
        self.stop_spinner()
        if simple_call is not None:
            print('Hooray, envmgr is correctly configured.')

