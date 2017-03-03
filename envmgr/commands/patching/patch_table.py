# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os

from tabulate import tabulate

def patch_table(patches, get_status):
    table_data = map(lambda p: {
        0: p.get('server_name'),
        1: p.get('to_ami'),
        2: p.get('instances_count'),
        3: p.get('scale_up_count'),
        4: get_status(p)
        }, patches)
    
    headers = {0:'ASG', 1:'Target AMI', 2:'Size', 3:'Scale out', 4:'Status'}
    return os.linesep + tabulate(table_data, headers, tablefmt="simple") + os.linesep
