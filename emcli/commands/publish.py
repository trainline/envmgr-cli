# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
import math

from envmgr import Service
from emcli.commands.base import BaseCommand

class PublishCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(PublishCommand, self).__init__(options, *args, **kwargs)
        self._register('publish', self.publish_service_file)

    def publish_service_file(self, service, version, file):
        file_path = os.path.abspath(file)
        if not os.path.isfile(file_path):
            print("{0} is not a valid file".format(file))
            return

        svc = Service(service) 
        file_size = self.convert_size(os.path.getsize(file_path))
        with open(file_path, 'rb') as file:
            result = svc.publish(file, version)
        
        if result is True:
            self.show_result({'success':True}, '{0} {1} published {2}'.format(service, version, file_size))
        else:
            self.show_result({'success':False}, 'There was an issue publishing this service')

    def convert_size(self, size_bytes):
        if (size_bytes == 0):
            return '0B'
        size_name = ("bytes", "Kb", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes/p, 2)
        return '%s %s' % (s, size_name[i])


