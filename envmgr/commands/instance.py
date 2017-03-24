# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import json

from envmgr.commands.base import BaseCommand
from repoze.lru import lru_cache

class Instance(BaseCommand):

    def run(self):	
        self.show_activity()
        self.describe_old_instances(**self.cli_args)

    def describe_old_instances(self, env, age):
        instances = self.api.get_instances(env)
        self.amis = self.api.get_images()
        age = int(age)
        matchers = [
            lambda ami,instance: ami.get('ImageId') == instance.get('ImageId'),
            lambda ami,instance: int(ami.get('DaysBehindLatest', 0)) >= age
        ]
        
        old_instances = [ instance for instance in instances if 
            any(ami for ami in self.amis if all([ match(ami,instance) for match in matchers ]) )
        ]

        old_instances = map(self.get_instance_info, old_instances)
        self.show_result(old_instances, old_instances)

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
