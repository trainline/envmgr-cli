"""ASG commands"""

import time

from envmgr.commands.base import BaseCommand

class ASG(BaseCommand):

    def run(self):
        if self.cmds['schedule']:
            self.schedule(**self.cli_args)
        elif self.cmds['wait-for']:
            self.wait(**self.cli_args)
        else:
            print("Unknown ASG command")


    def schedule(self, env, name):        
        data = {'propagateToInstances':True}

        if self.cmds['on']:
            data['schedule'] = 'ON'
        elif self.cmds['off']:
            data['schedule'] = 'OFF'
        elif self.cmds['default']:
            data['schedule'] = ''
        else:
            data['schedule'] = self.opts['cron']

        params = {'environment':env, 'asgname':name, 'data':data}
        result = self.api.put_asg_scaling_schedule(**params)

        n = len(result['ChangedInstances'])
        i = 'instance' if n == 1 else 'instances'
        s = 'default' if self.cmds['default'] else data['schedule']
        
        print("Scheduled {0} {1} in {2} to: {3}".format(n, i, name, s))


    def wait(self, env, name):
        while True:
            result = self.api.get_asg_ready(env, name)
            if result["ReadyToDeploy"]:
                print("{0} is ready for deployments".format(name))
                return
            else:
                print("Waiting for {0}...".format(name))
                time.sleep(10)

