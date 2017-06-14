# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time

from envmgr import ASG
from emcli.commands.base import BaseCommand
from emcli.commands.utils.asg_health import describe_asg_health

class AsgCommand(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(AsgCommand, self).__init__(options, *args, **kwargs)
        self._register(('get', 'schedule'), self.describe_schedule)
        self._register(('set', 'schedule'), self.update_schedule)
        self._register('health', self.describe_health)
        self._register('status', self.get_status)
        self._register('check', self.check_exists)
        self._register('wait-for', self.wait_for, False)

    def check_exists(self, env, name):
        asg = ASG(name, env)
        exists = asg.exists()
        self.show_result({'exists':exists}, exists)

    def describe_schedule(self, env, name):
        asg = ASG(name, env)
        schedule = asg.get_schedule()
        if not schedule:
            self.show_result({}, "No ASG schedule set")
        else:
            schedule_value = schedule.get('Value')
            if not schedule_value:
                schedule_value = 'default'
            self.show_result(schedule, "Schedule for {0} in {1} is {2}".format(name, env, schedule_value))

    def describe_health(self, env, name):
        asg = ASG(name, env)
        health = asg.get_health()
        if health.get('is_healthy'):
            n_services = health.get('required_count')
            n_instances = health.get('instances_count')
            message = '{0} is healthy ({1} services on {2} instances)'.format(name, n_services, n_instances)
        else:
            description = describe_asg_health(result)
            message = '{0} is not healthy: {1}'.format(name, description)
        self.show_result(health, message)

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

        asg = ASG(name, env)
        result = asg.set_schedule(schedule)
        n = len(list(result.get('ChangedInstances')))
        i = 'instance' if n == 1 else 'instances'
        s = 'default' if self.cmds.get('default') else schedule
        self.show_result(result, "Scheduled {0} {1} in {2} to: {3}".format(n, i, name, s))

    def get_status(self, env, name):
        asg = ASG(name, env)
        result = asg.get_status()
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
        start = time.time()
        timeout = int(self.opts.get('timeout', 0))
        should_continue = True
        while should_continue:
            elapsed = int(time.time() - start)
            if timeout is not 0 and elapsed > timeout:
                self.show_result({}, "Timeout exceeded")
                should_continue = False
            else:
                is_ready = self.get_status(env, name)
                if is_ready:
                    return
                else:
                    time.sleep(10)

