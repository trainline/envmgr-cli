# encoding=utf8
# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import json
import os

from envmgr import Instance
from emcli.commands.patching.patch_file import PatchFile
from emcli.commands.base import BaseCommand
from operator import attrgetter
from tabulate import tabulate

class InstanceCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(InstanceCommand, self).__init__(options, *args, **kwargs)
        self._register(('date'), self.describe_old_instances)

    def describe_old_instances(self, age):
        env = self.opts.get('env')
        cluster = self.opts.get('cluster')
        account = self.opts.get('account')
        result = Instance.get_instances_by_ami_age(age, env, cluster, account)
        sort_key = self.opts.get('sort')

        if sort_key is not None:
            reverse = True if sort_key == 'age' or sort_key == 'ami_age' else False
            result = sorted(result, key=attrgetter(sort_key), reverse=reverse)

        def truncate(s, l):
            return (s[:l - 1] + '…'.decode('utf-8')) if len(s) > l else s

        table_data = map(lambda i: {
            0: i.env,
            1: i.age,
            2: i.cluster,
            3: truncate(i.role, 22),
            4: i.type,
            5: i.id,
            6: i.ami_name,
            7: i.ami_age,
            8: i.state,
            }, result)
        
        headers = {0:'Env', 1:'Age', 2:'Cluster', 3:'Role', 4:'Type', 5:'Instance ID', 6:'AMI ', 7:'Age', 8:'State'}
        msg = os.linesep + tabulate(table_data, headers, tablefmt="simple") + os.linesep
        self.show_result(result, msg)
        if self.opts.get('report'):
            filepath = self.write_report(result, age)
            print('Report saved to {0}'.format(filepath))

    def write_report(self, content, age):
        filepath = os.path.join(os.getcwd(), 'instances_older_than_{0}_days.json'.format(age))
        with PatchFile.safe_open_w(filepath) as f:
            f.write(str(json.dumps(content, ensure_ascii=False)))
        return filepath

