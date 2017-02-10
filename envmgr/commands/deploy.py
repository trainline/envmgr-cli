"""Deploy a service"""

import time

from json import dumps
from envmgr.commands.base import BaseCommand

class Deploy(BaseCommand):

    def run(self):
        if self.cmds["wait-for"]:
            self.wait_for_deployment(**self.cli_args)
        elif self.cmds["status"]:
            self.get_deploy_status(**self.cli_args)
        else:
            self.deploy_service(**self.cli_args)

    def deploy_service(self, service, version, env, slice=None):
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

        if self.opts['dry-run']:
            dry_run = 'true'
        else:
            dry_run = 'false'

        result = self.api.post_deployments(dry_run, data)

        if dry_run == 'true':
            self.show_result(result, "Deployment dry run was successful")
        else:
            self.show_result(result, result['id'])

    def get_deploy_status(self, deploy_id):
        result = self.api.get_deployment(deploy_id)
        self.show_result(result, "Deployment: {0}".format(result['Value']['Status']))
        return result

    def wait_for_deployment(self, deploy_id):
        while True:
            result = self.get_deploy_status(deploy_id)
            status = result['Value']['Status']
            if status == "Failed" or status == "Success":
                return
            else:
                time.sleep(10)
