# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import responses
import os

from unittest import TestCase
from envmgr.commands import ASG
from mock import patch
from nose_parameterized import parameterized
from .helpers.api_test_case import APITestCase
from .helpers.utils import MOCK_ENV_VARS, mock_asg, mock_asg_tag

SCHEDULE_VALUES = [
    'ON', 'OFF', 'Start: * * * 5', 'Start: * * 2 *; Stop: * * 4 *' ]

class ASGTest(APITestCase):

    @responses.activate
    @patch.dict(os.environ, MOCK_ENV_VARS)
    def test_get_schedule_handles_no_tags(self):        
        self.setup_responses({})
        sut = ASG({})
        result = sut.get_schedule('prod', 'my-asg')
        self.assertEqual(result, {})
    
    @responses.activate
    @patch.dict(os.environ, MOCK_ENV_VARS)
    def test_get_schedule_handles_no_schedule(self):
        asg = mock_asg()
        self.setup_responses(asg)
        sut = ASG({})
        result = sut.get_schedule('prod', 'my-asg')
        self.assertEqual(result, {})

    @parameterized.expand( SCHEDULE_VALUES )
    @responses.activate
    @patch.dict(os.environ, MOCK_ENV_VARS)
    def test_get_schedule_returns_schedule_tag(self, schedule_value):
        asg = mock_asg()
        schedule = mock_asg_tag('Schedule', schedule_value)
        asg.get('Tags').append(schedule)
        self.setup_responses(asg)
        sut = ASG({})
        result = sut.get_schedule('prod', 'my-asg')
        self.assertEqual(result, schedule)

    @parameterized.expand( SCHEDULE_VALUES )
    @patch.dict(os.environ, MOCK_ENV_VARS)
    @patch('environment_manager.EMApi.put_asg_scaling_schedule')
    def test_set_schedule(self, schedule_value, put_asg_scaling_schedule):
        sut = ASG({})
        env = 'staging'
        asg_name = 'mock-asg'
        schedule = schedule_value
        result = sut.set_schedule(env, asg_name, schedule)
        put_asg_scaling_schedule.assert_called_with(
            asgname=asg_name,
            environment=env,
            data = {
                'schedule':schedule_value,
                'propagateToInstances': True
            }
        )

    def setup_responses(self, asg_response):
        self.mock_authentication()
        self.mock_response(r'/asgs/[\w\.\-]+', asg_response)

