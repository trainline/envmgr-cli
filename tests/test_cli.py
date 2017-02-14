# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import sys

from unittest import TestCase
from mock import patch
from envmgr.cli import main

class TestCLI(TestCase):

    @patch('envmgr.cli.Service.run')
    def test_get_service_health(self, run):
        self.assert_command('get MockService health in mk-1', run)

    @patch('envmgr.cli.Service.run')
    def test_get_service_health_with_slice(self, run):
        self.assert_command('get AcmeService health in mk-2 green', run)
    
    @patch('envmgr.cli.Service.run')
    def test_get_service_active_slice(self, run):
        self.assert_command('get CoolService active slice in mk-22', run)

    @patch('envmgr.cli.Service.run')
    def test_get_service_inactive_slice(self, run):
        self.assert_command('get CoolService inactive slice in mk-22', run)
    
    @patch('envmgr.cli.Service.run')
    def test_wait_for_healthy_service(self, run):
        self.assert_command('wait-for healthy CoolService in mk-22', run)
    
    @patch('envmgr.cli.ASG.run')
    def test_get_asg_status(self, run):
        self.assert_command('get asg mk-auto-scale status in mk-22', run)
    
    @patch('envmgr.cli.ASG.run')
    def test_get_asg_schedule(self, run):
        self.assert_command('get asg mk-auto-scale schedule in mk-22', run)
    
    @patch('envmgr.cli.ASG.run')
    def test_wait_for_asg(self, run):
        self.assert_command('wait-for asg mk-auto-scale in mk-22', run)
    
    @patch('envmgr.cli.ASG.run')
    def test_schedule_asg(self, run):
        self.assert_command('schedule asg mk-auto-scale on in mk-22', run)
    
    @patch('envmgr.cli.Deploy.run')
    def test_deploy_service(self, run):
        self.assert_command('deploy MyService 1.4.0 in prod-1', run)
    
    @patch('envmgr.cli.Deploy.run')
    def test_get_deploy_status(self, run):
        self.assert_command('get deploy status a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994', run)
    
    @patch('envmgr.cli.Deploy.run')
    def test_wait_for_deploy(self, run):
        self.assert_command('wait-for deploy a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994', run)
    
    @patch('envmgr.cli.Publish.run')
    def test_publish_service(self, run):
        self.assert_command('publish build-22.zip as AcmeService 1.2.3', run)
    
    @patch('envmgr.cli.Toggle.run')
    def test_toggle_service(self, run):
        self.assert_command('toggle MyService in mock-3', run)
    
    @patch('envmgr.cli.Patch.run')
    def test_get_patch_status(self, run):
        self.assert_command('get team-1 patch status in prod', run)

    def assert_command(self, cmd, func):
        argv = ['/usr/local/bin/envmgr'] + cmd.split(' ')
        with patch.object(sys, 'argv', argv):
            main()
            func.assert_called_once()

