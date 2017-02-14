# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

""" Patch Tests """

import responses
import random
import string

from unittest import TestCase
from envmgr.commands import Patch
from .apitestcase import APITestCase
from .utils import mock_server

class PatchTest(APITestCase):

    LATEST_STABLE_WINDOWS_APP = 'windows-2012r2-app-7.3.2'
    LATEST_STABLE_WINDOWS_SECURE = 'windows-2012r2-secureapp-7.3.0';

    @responses.activate
    def test_get_patch_requirements(self):
        cluster = 'acmeteam'
        rnd_servers = self.create_servers(cluster, 10)
        win_servers = self.create_servers(cluster, 2, self.LATEST_STABLE_WINDOWS_APP, True)
        old_win_servers = self.create_servers(cluster, 2, 'windows-2012r2-secureapp-7.0.0', False)
    
        self.setup_responses()
        self.respond_with_servers(rnd_servers + old_win_servers + win_servers)
        
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
