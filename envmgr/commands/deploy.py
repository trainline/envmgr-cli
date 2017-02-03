"""Publish a service package to S3"""

from json import dumps
from envmgr.commands.base import BaseCommand

class Deploy(BaseCommand):

    def run(self):

        self.deploy_overwrite_service(**self.cli_args)


    def deploy_overwrite_service(self, service, version, env, slice=None):        
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


    def deploy_blue_green_service(self, service, version, env, slice):
        print(service, version, env, slice)


