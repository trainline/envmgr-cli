# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import responses
import random
import string

from unittest import TestCase
from envmgr.commands import Patch
from nose_parameterized import parameterized, param
from .apitestcase import APITestCase
from .utils import mock_server
from .patch_scenarios import TEST_SCENARIOS

class PatchTest(APITestCase):

    @parameterized.expand( TEST_SCENARIOS )
    @responses.activate
    def test_identify_non_latest_stable(self, *args, **kwargs):
        patch_cluster = kwargs.get('patch_cluster')
        expected_result = kwargs.get('expected')
        servers_in_env = []

        # Create a list of servers in env, based on test scenario
        for server_desc in args:
            servers_in_env += self.create_servers(**server_desc)

        self.setup_responses()
        self.respond_with_servers(servers_in_env)

        sut = Patch({})        
        result = sut.get_patch_requirements(patch_cluster, 'staging')
        self.assertEqual(len(result), expected_result)
    

    def respond_with_servers(self, servers):
        server_response = {
            'EnvironmentName': 'staging',
            'Value': servers
        }
        self.mock_response(r'/environments/[\w\.\-]+/servers', server_response)

    def setup_responses(self):
        self.mock_authentication()
        self.mock_response_with_file(r'/images', 'ami_response.json')

    def create_servers(self, cluster, n=1, ami='mock-ami-1.0.0', latest=False):
        servers = [ mock_server(cluster, ami, latest) for x in range(n) ]
        return servers
