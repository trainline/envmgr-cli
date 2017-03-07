# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr.commands.base import BaseCommand

class Toggle(BaseCommand):

    def run(self):
        self.show_activity()
        self.toggle_service_slices(**self.cli_args)

    def toggle_service_slices(self, service, env):
        result = self.api.put_service_slices_toggle(service, env)
        self.show_result(result, "{0} was toggled in {1}".format(service, env))

