# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time

from envmgr.commands.base import BaseCommand

class ASG(BaseCommand):

    def run(self):
        if self.cmds.get('schedule'):
            if self.cmds.get('get'):
                self.describe_schedule(**self.cli_args)
            else:
                self.update_schedule(**self.cli_args)
        elif self.cmds.get('status'):
            self.get_status(**self.cli_args)
        elif self.cmds.get('wait-for'):
            self.wait_for(**self.cli_args)
        else:
            print("Unknown ASG command")

    def describe_schedule(self, env, name):
        result = self.get_schedule(env, name)
        if not result:
            self.show_result({}, "No ASG schedule set")
        else:
            self.show_result(result, "Schedule for {0} in {1} is {2}".format(name, env, result.get('Value')))

    def get_schedule(self, env, name):
        asg = self.api.get_asg(env, name)
        tags = asg.get('Tags')
        if tags is not None:
            schedule_tag = [ tag for tag in tags if tag.get('Key') == 'Schedule' ]
            if (len(schedule_tag) > 0):
                return schedule_tag[0]
        return {}

    def update_schedule(self, env, name):
        schedule = ''
        if self.cmds.get('on'):
            schedule = 'ON'
        elif self.cmds.get('off'):
            schedule = 'OFF'
        elif self.cmds.get('default'):
            schedule = ''
        else:
            schedule = self.opts.get('cron')

        result = self.set_schedule(env, name, schedule)
        n = len(list(result.get('ChangedInstances')))
        i = 'instance' if n == 1 else 'instances'
        s = 'default' if self.cmds.get('default') else data.get('schedule')
        self.show_result(result, "Scheduled {0} {1} in {2} to: {3}".format(n, i, name, s))

    def set_schedule(self, env, name, schedule):        
        data = {'propagateToInstances':True, 'schedule':schedule}
        params = {'environment':env, 'asgname':name, 'data':data}
        return self.api.put_asg_scaling_schedule(**params)

    def get_status(self, env, name):
        result = self.api.get_asg_ready(env, name)
        is_ready = result.get("ReadyToDeploy")

        if is_ready:
            self.show_result(result, "{0} is ready for deployments".format(name))
        else:
            n_total = result.get('InstancesTotalCount')
            states = map(lambda state,count: "{0}={1}".format(state, count), 
                    result.get('InstancesByLifecycleState').iteritems())
            self.show_result(result, "{0} is not ready for deployment (instances: {1}, Total={2})".format(name, ", ".join(states), n_total))

        return is_ready 

    def wait_for(self, env, name):
        while True:
            is_ready = self.get_status(env, name)
            if is_ready:
                return
            else:
                time.sleep(10)

