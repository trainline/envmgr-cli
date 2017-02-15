# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import responses
import random
import string

from unittest import TestCase
from envmgr.commands import Patch
from nose_parameterized import parameterized
from .apitestcase import APITestCase
from .utils import mock_server

class PatchTest(APITestCase):

    LATEST_STABLE_WINDOWS_APP = 'windows-2012r2-app-7.3.2'
    LATEST_STABLE_WINDOWS_SECURE = 'windows-2012r2-secureapp-7.3.0'
    LATEST_STABLE_UBUNTU = 'ubuntu-16.04-0.2.7'

    @parameterized.expand([
        ('5 Old Win', 5, 0, 0),
        ('3 Old Win, 7 Linux', 3, 0, 7),
        ('9 Old Win, 10 Latest Win, 6 Linux', 9, 10, 6),
        ('4 Old Win, 2 Latest Win', 4, 2, 0),
        ('3 Latest Win, 2 Linux', 0, 3, 2),
        ('15 Latest Win', 0, 3, 0),
        ('20 Linux', 0, 0, 22),
        ('400 Old Windows', 400, 0, 0),
        ('276 Old Win, 598 Latest Win, 1238 Linux', 276, 598, 1238),
        ('No Servers', 0, 0, 0)
    ])
    @responses.activate
    def test_identify_non_latest_stable(self, _, n_old_win, n_latest_win, n_linux):
        cluster = 'acmeteam'
        linux_servers = self.create_servers(cluster, n_linux, self.LATEST_STABLE_UBUNTU)
        win_servers = self.create_servers(cluster, n_latest_win, self.LATEST_STABLE_WINDOWS_APP, True)
        old_win_servers = self.create_servers(cluster, n_old_win, 'windows-2012r2-secureapp-7.0.0', False)
    
        self.setup_responses()
        self.respond_with_servers(linux_servers + old_win_servers + win_servers)
        sut = Patch({})        
        
        result = sut.get_patch_requirements(cluster, 'staging')
        self.assertEqual(len(result), len(old_win_servers))

    def respond_with_servers(self, servers):
        server_response = {
            'EnvironmentName': 'staging',
            'Value': servers
        }
        self.mock_response(r'/environments/[\w\.\-]+/servers', server_response)

    def setup_responses(self):
        self.mock_authentication()
        self.mock_response_with_file(r'/images', 'ami_response.json')

    def create_servers(self, cluster, n=1, ami='mock-ami-1.0.0', is_latest_stable=False):
        servers = [ mock_server(cluster, ami, is_latest_stable) for x in range(n) ]
        return servers
