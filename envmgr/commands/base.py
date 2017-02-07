"""The base command for handling command CLI / API logic"""

import os
import re
import json

from environment_manager import EMApi

class BaseCommand(object):

    def __init__(self, options, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.opts = {}
        self.cli_args = {}
        self.cmds = {}

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
        self.api = EMApi(server=host, user=user, password=pwrd, retries=1)


    def run(self):
        raise NotImplementedError('Subclass does not implement run')


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
        if self.opts['json']:
            print(json.dumps(result))
        elif isinstance(message, list):
            print(os.linesep.join(message))
        else:
            print(message)

