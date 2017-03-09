# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
import requests
import math

from json import dumps
from envmgr.commands.base import BaseCommand

class Publish(BaseCommand):

    def run(self):
        self.show_activity()
        self.publish_service_file(**self.cli_args)

    def publish_service_file(self, service, version, file):
        file_path = os.path.abspath(file)
        if not os.path.isfile(file_path):
            print("{0} is not a valid file".format(file))
            return

        file_size = self.convert_size(os.path.getsize(file_path))
        package_path = self.api.get_package_upload_url(service, version)
        if isinstance(package_path, dict):
            upload_url = package_path.get('url')
        else:
            upload_url = package_path

        with open(file_path,'rb') as payload:
            headers = {'content-type':'application/zip'}
            r = requests.put(upload_url, data=payload, headers=headers)
            if int(str(r.status_code)[:1]) == 2:
                self.show_result({}, "{0} v{1} published ({2})".format(service,version,file_size))
            else:
                self.show_result({}, "Error")

    def convert_size(self, size_bytes):
        if (size_bytes == 0):
            return '0B'
        size_name = ("bytes", "Kb", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes/p, 2)
        return '%s %s' % (s, size_name[i])


