"""ASG commands"""

import time

from envmgr.commands.base import BaseCommand

class ASG(BaseCommand):

    def run(self):
        if self.cmds['schedule']:
            self.schedule(**self.cli_args)
        elif self.cmds['status']:
            self.get_status(**self.cli_args)
        elif self.cmds['wait-for']:
            self.wait_for(**self.cli_args)
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
        
        self.show_result(result, "Scheduled {0} {1} in {2} to: {3}".format(n, i, name, s))


    def get_status(self, env, name):
        result = self.api.get_asg_ready(env, name)
        is_ready = result["ReadyToDeploy"]

        if is_ready:
            self.show_result(result, "{0} is ready for deployments".format(name))
        else:
            n_total = result['InstancesTotalCount']
            states = map(lambda (state,count): "{0}={1}".format(state, count), 
                    result['InstancesByLifecycleState'].iteritems())
            self.show_result(result, "{0} is not ready for deployment (instances: {1}, Total={2})".format(name, ", ".join(states), n_total))

        return is_ready 


    def wait_for(self, env, name):
        while True:
            is_ready = self.get_status(env, name)
            if is_ready:
                return
            else:
                time.sleep(10)

