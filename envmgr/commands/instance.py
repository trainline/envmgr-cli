# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import json
import os

from envmgr.commands.patching.patch_file import PatchFile
from envmgr.commands.base import BaseCommand
from repoze.lru import lru_cache
from tabulate import tabulate

class Instance(BaseCommand):

    def run(self):	
        self.show_activity()
        self.describe_old_instances(**self.cli_args)

    def describe_old_instances(self, age):
        result = self.get_old_instances(age)
        sort_key = self.opts.get('sort')
        
        if sort_key is not None:
            reverse = True if sort_key == 'age' else False
            result = sorted(result, key=lambda k: k[sort_key], reverse=reverse)

        table_data = map(lambda i: {
            0: i.get('cluster'),
            1: i.get('role'),
            2: i.get('id'),
            3: i.get('ami'),
            4: i.get('age'),
            5: i.get('state'),
            }, result)
        headers = {0:'Cluster', 1:'Role', 2:'Instance ID', 3:'AMI', 4:'Age', 5:'State'}
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
    
    def get_old_instances(self, age):
        env = self.opts.get('env')
        cluster = self.opts.get('cluster')
        account = self.opts.get('account')

        instances = self.api.get_instances(env, cluster, account)
        self.amis = self.api.get_images()
        age = int(age)
        matchers = [
            lambda ami,instance: ami.get('ImageId') == instance.get('ImageId'),
            lambda ami,instance: int(ami.get('DaysBehindLatest', 0)) >= age
        ]
        old_instances = [ instance for instance in instances if 
            any(ami for ami in self.amis if all([ match(ami,instance) for match in matchers ]) )
        ]
        return list(map(self.get_instance_info, old_instances))

    def get_instance_info(self, instance):
        tags = instance.get('Tags', [])
        (image, age) = self.get_ami_info(instance.get('ImageId'))
        return {
            'id': instance.get('InstanceId'),
            'type': instance.get('InstanceType'),
            'name': self.get_tag_value(tags, 'Name'),
            'role': self.get_tag_value(tags, 'Role'),
            'cluster': self.get_tag_value(tags, 'OwningCluster'),
            'state': instance.get('State').get('Name'),
            'ami': image,
            'age': age
        }

    @lru_cache(128)
    def get_ami_info(self, image_id):
        ami = [ ami for ami in self.amis if ami.get('ImageId') == image_id ]
        if ami:
            ami = ami[0]
        else:
            return None
        return (ami.get('Name'), ami.get('DaysBehindLatest'))


    def get_tag_value(self, tags, key):
        tag = [ tag.get('Value') for tag in tags if tag.get('Key') == key ]
        if tag:
            return tag[0]
