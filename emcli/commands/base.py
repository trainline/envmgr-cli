# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
import re
import json
import sys
import platform
import logging
import envmgr
import getpass

from base64 import b64encode
from future.utils import viewitems
from emcli.commands.spinner import Spinner
from emcli import __version__ as VERSION

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
        self.register = {}
        user_agent = BaseCommand.get_user_agent()

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

        safe_log_opts = {k: v for k, v in viewitems(self.opts) if k != 'pass' }
    
        logging.debug('Args: {0}'.format(self.cli_args))
        logging.debug('Opts: {0}'.format(safe_log_opts))
        logging.debug('User-Agent: {0}'.format(user_agent))

        host = self.get_config('host', 'ENVMGR_HOST')
        user = self.get_config('user', 'ENVMGR_USER')
        pwrd = self.get_password('pass', 'ENVMGR_PASS')
        headers = {'User-Agent':user_agent}
        envmgr.config(host, user, b64encode(pwrd.encode('ascii')), default_headers=headers)

    def _register(self, cmd, action, with_spinner=True):
        """
        Register a method to run when the given set of commands are matched
        """
        self.register[cmd] = (action, with_spinner)

    def run(self):
        command = None

        def match_command(cmd):
            q = cmd.split('!')
            if len(q) is 1:
                return self.cmds.get(cmd)
            elif len(q) is 2:
                return not self.cmds.get(q[1])
            else:
                raise Exception('Unknown command matcher: {0}'.format(cmd))

        for key in self.register:
            if isinstance(key, tuple):
                if all([ match_command(cmd) for cmd in key ]):
                    command = self.register[key]
            else:
                if self.cmds.get(key):
                    command = self.register[key]
        if command is not None:
            (action, with_spinner) = command
            if with_spinner:
                self.show_activity()
            action(**self.cli_args)
        else:
            raise Exception('Unknown command')

    def show_activity(self):
        if not self.opts.get('json') and not self.opts.get('ci-mode'):
            self.spinner = Spinner()
            self.spinner.start()

    def stop_spinner(self):
        if not self.opts.get('json') and not self.opts.get('ci-mode') and self.spinner is not None:
            self.spinner.stop()

    def get_password(self, option, env_name):
        password = self.get_config(option, env_name, required=self.opts.get('ci-mode'))
        if password is None:
            password = getpass.getpass()
        return password

    def get_config(self, option, env_name, required=True):
        value = None
        if option in self.opts:
            value = self.opts[option]
        else:
            value = os.getenv(env_name)

        if required and value is None:
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

