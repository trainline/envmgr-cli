# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time
import sys

from envmgr import Service
from json import dumps
from emcli.commands.base import BaseCommand

class DeployCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(DeployCommand, self).__init__(options, *args, **kwargs)
        self._register('wait-for', self.wait_for_deployment, False)
        self._register('status', self.get_deploy_status)
        self._register(('deploy','in'), self.deploy_service)

    def deploy_service(self, service, version, env, slice=None):
        dry_run = self.opts.get('dry-run', False)
        role = self.opts.get('role', None)
        svc = Service(service, env, version)
        result = svc.deploy(slice=slice, dry_run=dry_run, role=role)

        if dry_run:
            self.show_result(result, "Deployment dry run was successful")
        else:
            self.show_result(result, result.get('id'))

    def get_deploy_status(self, deploy_id):
        result = Service.get_deployment_by_id(deploy_id)
        self.show_result(result, "Deployment: {0}".format(result.get('Value').get('Status')))
        return result

    def wait_for_deployment(self, deploy_id):
        while True:
            result = self.get_deploy_status(deploy_id)
            status = result.get('Value').get('Status')
            if status == "Failed" and self.opts.get('ci-mode'):
                sys.exit(1)
            elif status == "Failed" or status == "Success":
                return
            else:
                time.sleep(10)
