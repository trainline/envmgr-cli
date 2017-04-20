# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

def describe_asg_health(asg_status):
    if asg_status.get('required_count') == 0: 
        return 'No services expected'
    elif asg_status.get('missing_count') is not None:
        return 'Missing services'
    elif asg_status.get('unexpected_count') is not None:
        return 'Unexpected services'
    elif asg_status.get('instances_count') == 0:
        return 'No instances'
    else:
        return 'Instances not ready'

