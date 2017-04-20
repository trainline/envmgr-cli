# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os

from emcli.commands.utils.asg_health import describe_asg_health
from tabulate import tabulate

def get_default_status(p):
    if p.get('has_standby_instances'):
        return 'Instances in standby'
    elif p.get('unhealthy') is not None:
        return describe_asg_health(p.get('unhealthy'))
    elif p.get('invalid_ami'):
        return 'Invalid AMI data'
    elif p.get('warning'):
        return 'Warning' 
    else:
        return ''

def patch_table(patches, get_status=get_default_status):
    table_data = map(lambda p: {
        0: p.get('server_name'),
        1: p.get('ami_type'),
        2: p.get('current_version'),
        3: p.get('target_version'),
        4: p.get('instances_count'),
        5: p.get('scale_up_count'),
        6: get_status(p)
        }, patches)
    
    headers = {0:'ASG', 1:'AMI Type', 2:'Current', 3:'Target', 4:'Instances', 5:'Scale out', 6:'Status'}
    return os.linesep + tabulate(table_data, headers, tablefmt="simple") + os.linesep

