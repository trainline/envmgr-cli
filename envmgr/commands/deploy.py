# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time

from json import dumps
from envmgr.commands.base import BaseCommand

class Deploy(BaseCommand):

    def run(self):
        self.show_activity()
        if self.cmds.get("wait-for"):
            self.wait_for_deployment(**self.cli_args)
        elif self.cmds.get("status"):
            self.get_deploy_status(**self.cli_args)
        else:
            self.deploy_service(**self.cli_args)

    def deploy_service(self, service, version, env, slice=None):
        is_dry_run = self.opts.get('dry-run') == True
        result = self.create_deployment(service, version, env, slice, is_dry_run)
        if is_dry_run:
            self.show_result(result, "Deployment dry run was successful")
        else:
            self.show_result(result, result['id'])

    def create_deployment(self, service, version, env, slice, is_dry_run):
        data = {
            'environment': env,
            'service': service,
            'version': version,
        }

        if slice is not None:
            data['slice'] = slice
            data['mode'] = 'bg'
        else:
            data['mode'] = 'overwrite'

        dry_run = 'true' if is_dry_run else 'false'
        return self.api.post_deployments(dry_run, data)

    def get_deploy_status(self, deploy_id):
        result = self.api.get_deployment(deploy_id)
        self.show_result(result, "Deployment: {0}".format(result.get('Value').get('Status')))
        return result

    def wait_for_deployment(self, deploy_id):
        while True:
            result = self.get_deploy_status(deploy_id)
            status = result.get('Value').get('Status')
            if status == "Failed" or status == "Success":
                return
            else:
                time.sleep(10)
