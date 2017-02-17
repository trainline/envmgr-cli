# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import responses
import os

from unittest import TestCase
from envmgr.commands import Deploy
from mock import patch
from nose_parameterized import parameterized
from .helpers.api_test_case import APITestCase
from .helpers.utils import MOCK_ENV_VARS
from .helpers.deploy_scenarios import DEPLOY_SCENARIOS

class DeployTest(APITestCase):

    @parameterized.expand( DEPLOY_SCENARIOS )
    @patch.dict(os.environ, MOCK_ENV_VARS)
    @patch('environment_manager.EMApi.post_deployments')
    def test_create_deployment_bg_mode(self, dry_run, deploy_data, expected, post_deployments):
        sut = Deploy({})
        expected_dry_run_value = 'false'
        if dry_run:
            sut.opts['dry-run'] = True
            expected_dry_run_value = 'true'

        expected_result = deploy_data.copy()
        expected_result.update(expected)
        expected_result['environment'] = expected_result.get('env')
        expected_result.pop('env')

        result = sut.deploy_service(**deploy_data)
        post_deployments.assert_called_with(expected_dry_run_value, expected_result)

