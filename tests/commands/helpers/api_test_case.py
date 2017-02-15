# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

""" Base API Test Class """

import sys
import re
import responses
import json

from codecs import open
from os.path import abspath, dirname, join
from unittest import TestCase

class APITestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(APITestCase, self).__init__(*args, **kwargs)

    def mock_response_with_file(self, path_match, file_name):
        response = self.load_json_data(file_name)
        self.mock_response(path_match, response)

    def mock_response(self, path_match, response):
        response_data = json.dumps(response)
        url_match = re.compile(r'https?://[\w\.]+/api/v1' + path_match)
        
        responses.add(responses.GET, url_match, match_querystring=True,
                body=response_data, status=200, content_type='application/json')

    def load_json_data(self, file_name):
        this_dir = abspath(dirname(__file__))
        
        with open(join(this_dir, '../data/', file_name), encoding='utf-8') as file_data:
            json_data = json.load(file_data)
        
        return json_data

    def mock_authentication(self):
        token_url = re.compile(r'https?://[\w\.]+/api/token')
        
        responses.add(responses.POST, token_url, match_querystring=True,
                body='mock-token', status=200, content_type='text/plain')

