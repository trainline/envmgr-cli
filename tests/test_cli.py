# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import sys
import os

from unittest import TestCase
from mock import patch
from emcli.cli import main, except_hook
from nose_parameterized import parameterized

TEST_COMMANDS = [
    ('get MockService health in prod',                      'emcli.cli.ServiceCommand.run'),
    ('get AcmeService health in prod green',                'emcli.cli.ServiceCommand.run'),
    ('get CoolService active slice in dev',                 'emcli.cli.ServiceCommand.run'),
    ('get CoolService inactive slice in staging',           'emcli.cli.ServiceCommand.run'),
    ('wait-for healthy CoolService in prod',                'emcli.cli.ServiceCommand.run'),
    ('check asg mock-asg exists in prod',                   'emcli.cli.AsgCommand.run'),
    ('get asg mock-asg status in prod',                     'emcli.cli.AsgCommand.run'),
    ('get asg mock-asg schedule in staging',                'emcli.cli.AsgCommand.run'),
    ('get asg mock-asg health in test',                     'emcli.cli.AsgCommand.run'),
    ('wait-for asg mock-asg in prod',                       'emcli.cli.AsgCommand.run'),
    ('set asg mock-asg schedule off in staging',            'emcli.cli.AsgCommand.run'),
    ('get instances out of date by 30 days --env=prod',     'emcli.cli.InstanceCommand.run'),
    ('deploy MyService 1.4.0 in prod',                      'emcli.cli.DeployCommand.run'),
    ('get deploy status a2fbb0c0-ed4c-11e6-85b1',           'emcli.cli.DeployCommand.run'),
    ('wait-for deploy a2fbb0c0-ed4c-11e6-85b1',             'emcli.cli.DeployCommand.run'),
    ('publish build-22.zip as AcmeService 1.2.3',           'emcli.cli.PublishCommand.run'),
    ('publish --env MyEnv build-22.zip as AcmeService 1.2.3',           'emcli.cli.PublishCommand.run'),
    ('toggle MyService in staging',                         'emcli.cli.ToggleCommand.run'),
    ('get upstream status for blue MyService in staging',   'emcli.cli.ToggleCommand.run'),
    ('wait-for toggle to blue MyService in staging',        'emcli.cli.ToggleCommand.run'),
    ('get A-team patch status in prod',                     'emcli.cli.PatchCommand.run'),
    ('patch team in prod',                                  'emcli.cli.PatchCommand.run'),
    ('get team asg cycle status in staging',                'emcli.cli.CycleCommand.run'),
    ('cycle team asgs in prod',                             'emcli.cli.CycleCommand.run'),
    ('verify',                                              'emcli.cli.VerifyCommand.run')
]

og_getenv = os.getenv

def no_env_config(*args):
    var_name = args[0]
    if var_name.startswith('ENVMGR_'):
        return None
    else:
        return og_getenv(var_name, '')

class TestCLI(TestCase):

    @parameterized.expand( TEST_COMMANDS )
    def test_command(self, cmd, expected_call):
        with patch(expected_call) as run:
            self.assert_command_with_default_opts(cmd, run)

    @parameterized.expand( TEST_COMMANDS )
    def test_command_with_json(self, cmd, expected_call):
        with patch(expected_call) as run:
            self.assert_command_with_default_opts(cmd + ' --json', run)

    @parameterized.expand( TEST_COMMANDS )
    @patch('os.getenv', wraps=no_env_config)
    def test_command_without_password(self, cmd, expected_call, getenv):
        with patch(expected_call) as run:
            self.assert_command_with_no_pass(cmd, run)

    @patch('getpass.getpass', return_value='pa$$word')
    def assert_command_with_no_pass(self, cmd, func, getpass):
        required_opts = '--host=acme.com --user=roadrunner'
        argv = ['/usr/local/bin/envmgr'] + cmd.split(' ') + required_opts.split(' ')
        with patch.object(sys, 'argv', argv):
            main()
            getpass.assert_called_once()

    def test_custom_except_hook(self):
        self.assertEqual(sys.excepthook, except_hook)
    
    def assert_command_with_default_opts(self, cmd, func):
        required_opts = '--host=acme.com --user=roadrunner --pass=pa$$word'
        self.assert_command(cmd, func, required_opts)

    def assert_command(self, cmd, func, required_opts):
        argv = ['/usr/local/bin/envmgr'] + cmd.split(' ') + required_opts.split(' ')
        with patch.object(sys, 'argv', argv):
            main()
            func.assert_called_once()

