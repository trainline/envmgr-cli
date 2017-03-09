# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
import re
import json
import sys
import platform

from environment_manager import EMApi
from envmgr.commands.spinner import Spinner
from envmgr import __version__ as VERSION

class BaseCommand(object):

    @staticmethod
    def get_user_agent():
        system = platform.system()
        machine = platform.machine()
        python_v = '.'.join(map(str, (sys.version_info)[:3]))
        return 'envmgr-cli/{0} ({1} {2}) Python/{3}'.format(VERSION, system, machine, python_v)

    def __init__(self, options, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.opts = {}
        self.cli_args = {}
        self.cmds = {}
        self.spinner = None

        for (k, v) in options.items():
            if v is not None:
                cli_arg = re.search('\<([\w\-]+)\>', k)
                cli_opt = re.search('^\-\-([a-zA-Z0-9]+[\w\-]+)', k)

                if cli_arg is not None:
                    self.cli_args[cli_arg.group(1)] = v
                elif cli_opt is not None:
                    self.opts[cli_opt.group(1)] = v
                else:
                    self.cmds[k] = v

        host = self.get_config('host', 'ENVMGR_HOST')
        user = self.get_config('user', 'ENVMGR_USER')
        pwrd = self.get_config('pass', 'ENVMGR_PASS')
        headers = {'User-Agent':BaseCommand.get_user_agent()}
        self.api = EMApi(server=host, user=user, password=pwrd, retries=1, default_headers=headers)

    def run(self):
        raise NotImplementedError('Subclass does not implement run')

    def show_activity(self):
        if not self.opts.get('json'):
            self.spinner = Spinner()
            self.spinner.start()

    def stop_spinner(self):
        if not self.opts.get('json') and self.spinner is not None:
            self.spinner.stop()

    def get_config(self, option, env_name):
        value = None
        if option in self.opts:
            value = self.opts[option]
        else:
            value = os.getenv(env_name)

        if value is None:
            raise ValueError("--{0} was not given and no {1} value is set.".format(option, env_name))
        else:
            return value

    def show_result(self, result, message):
        self.stop_spinner()
        if self.opts.get('json'):
            print(json.dumps(result))
        elif isinstance(message, list):
            print(os.linesep.join(message))
        else:
            print(message)

