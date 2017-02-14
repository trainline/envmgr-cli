# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import random
import string

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

