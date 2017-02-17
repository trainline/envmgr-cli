# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

""" Base API Test Class """

import sys
import re
import responses
import json

from unittest import TestCase
from .utils import load_json_data

class APITestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(APITestCase, self).__init__(*args, **kwargs)

    def mock_response_with_file(self, path_match, file_name):
        response = load_json_data(file_name)
        self.mock_response(path_match, response)

    def mock_response(self, path_match, response):
        response_data = json.dumps(response)
        url_match = re.compile(r'https?://[\w\.]+/api/v1' + path_match)
        
        responses.add(responses.GET, url_match, match_querystring=True,
                body=response_data, status=200, content_type='application/json')

    def mock_authentication(self):
        token_url = re.compile(r'https?://[\w\.]+/api/v1/token')
        
        responses.add(responses.POST, token_url, match_querystring=True,
                body='mock-token', status=200, content_type='text/plain')

