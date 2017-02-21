# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import sys

from unittest import TestCase
from mock import patch
from envmgr.cli import main, except_hook
from nose_parameterized import parameterized

TEST_COMMANDS = [
    ('get MockService health in prod',              'envmgr.cli.Service.run'),
    ('get AcmeService health in prod green',        'envmgr.cli.Service.run'),
    ('get CoolService active slice in dev',         'envmgr.cli.Service.run'),
    ('get CoolService inactive slice in staging',   'envmgr.cli.Service.run'),
    ('wait-for healthy CoolService in prod',        'envmgr.cli.Service.run'),
    ('get asg mock-asg status in prod',             'envmgr.cli.ASG.run'),
    ('get asg mock-asg health in test',             'envmgr.cli.ASG.run'),
    ('get asg mock-asg schedule in staging',        'envmgr.cli.ASG.run'),
    ('wait-for asg mock-asg in prod',               'envmgr.cli.ASG.run'),
    ('schedule asg mock-asg off in staging',        'envmgr.cli.ASG.run'),
    ('deploy MyService 1.4.0 in prod',              'envmgr.cli.Deploy.run'),
    ('get deploy status a2fbb0c0-ed4c-11e6-85b1',   'envmgr.cli.Deploy.run'),
    ('wait-for deploy a2fbb0c0-ed4c-11e6-85b1',     'envmgr.cli.Deploy.run'),
    ('publish build-22.zip as AcmeService 1.2.3',   'envmgr.cli.Publish.run'),
    ('toggle MyService in staging',                 'envmgr.cli.Toggle.run'),
    ('get A-team patch status in prod',             'envmgr.cli.Patch.run'),
]

class TestCLI(TestCase):

    @parameterized.expand( TEST_COMMANDS )
    def test_command(self, cmd, expected_call):
        with patch(expected_call) as run:
            self.assert_command(cmd, run)

    @parameterized.expand( TEST_COMMANDS )
    def test_command_with_json(self, cmd, expected_call):
        with patch(expected_call) as run:
            self.assert_command(cmd + ' --json', run)
    
    def test_custom_except_hook(self):
        self.assertEqual(sys.excepthook, except_hook)

    def assert_command(self, cmd, func):
        required_opts = '--host=acme.com --user=roadrunner --pass=pa$$word'
        argv = ['/usr/local/bin/envmgr'] + cmd.split(' ') + required_opts.split(' ')
        with patch.object(sys, 'argv', argv):
            main()
            func.assert_called_once()

