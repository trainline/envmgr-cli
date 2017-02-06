"""Publish a service package to S3"""

from json import dumps
from envmgr.commands.base import BaseCommand

class Deploy(BaseCommand):

    def run(self):
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

        dry_run = "true" if 'dry-run' in self.opts else "false"
        result = self.api.post_deployments(dry_run, data)
        print(result)

    
    def get_deploy_status(self, deploy_id):
        result = self.api.get_deployment(deploy_id)
        self.show_result(result, "Status: {0}".format(result['Value']['Status']))
