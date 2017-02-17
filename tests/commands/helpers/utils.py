# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import random
import string
import json

from codecs import open
from os.path import abspath, dirname, join

MOCK_ENV_VARS = {
    'ENVMGR_HOST':'envmgr.acme.com',
    'ENVMGR_USER':'roadrunner',
    'ENVMGR_PASS':'meepmeep'
}

def load_json_data(file_name):
    this_dir = abspath(dirname(__file__))
    with open(join(this_dir, '../../data/', file_name), encoding='utf-8') as file_data:
        json_data = json.load(file_data)
    return json_data

def mock_asg():
    name = 'asg-{0}'.format(rand_str())
    arn = 'arn:aws:autoscaling:eu-west-1:123456789012:asg:{0}/mock'.format(rand_str())
    return {
        'AutoScalingGroupName': name,
        'AutoScalingGroupARN': arn,
        'Tags': [ mock_asg_tag('SecurityZone', 'Other') ]
    }

def mock_asg_tag(key, value):
    return {
        'ResourceId': 'envmgr-cli-mock',
        'ResourceType': 'auto-scaling-group',
        'Key': key,
        'Value': value,
        'PropagateAtLaunch': True
    }

def mock_server(cluster, ami_name, is_latest_stable, current=1, desired=1):
    rnd = rand_str()
    name = 'mock-server-{0}'.format(rnd)
    role = 'mock-role-{0}'.format(rnd)
    service = 'mock-service-{0}'.format(rnd)
    server = {
        'Name': name,
        'Role': role,
        'Cluster': cluster,
        'Schedule': 'ON',
        'IsBeingDeleted': False,
        'Services': [ service ],
        'Ami': {
            'Name': ami_name,
            'IsLatestStable': is_latest_stable
        },
        'Size': {
            'Current': current,
            'Desired': desired
        }
    }
    return server

def rand_str(length=8):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))

