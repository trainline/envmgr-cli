# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import datetime

from envmgr import ASG
from emcli.commands.patching.patch_states import PatchStates
from emcli.commands.patching.patch_file import PatchFile

class PatchProcess(object):

    def __init__(self, api, operation, is_refresh=False):
        self.api = api
        self.operation = operation
        self.cluster = operation.get('cluster')
        self.env = operation.get('env')
        self.is_refresh = is_refresh

    def update_launch_configs(self, patches):
        if not patches:
            return
        # Update Launch Configs
        for patch in patches:
            asg_name = patch.get('server_name')
            data = {'AMI':patch.get('new_ami_id')}
            update = self.api.put_asg_launch_config(self.env, asg_name, data)
            self.update_patch_status(patch, PatchStates.STATE_LC_UPDATED)
        
    def set_scale_out_size(self, patches):
        if not patches:
            return
        # Set scale out target size
        for patch in patches:
            size = patch.get('scale_up_count')
            asg_name = patch.get('server_name')
            data = {'desired':size, 'max':size}
            update = self.api.put_asg_size(self.env, asg_name, data)
            self.update_patch_status(patch, PatchStates.STATE_SCALE_OUT_TARGET_SET)

    def monitor_scale_out(self, patches):
        if not patches:
            return
        def has_scaled_out(patch):
            result = self.api.get_asg_ready(self.env, patch.get('server_name'))
            return result.get('ReadyToDeploy') is True

        scaled_out_asgs = [ patch for patch in patches if has_scaled_out(patch) ]
        for patch in scaled_out_asgs:
            self.update_patch_status(patch, PatchStates.STATE_SCALED_OUT, False)
        self.write_to_file()

    def monitor_service_installation(self, patches):
        if not patches:
            return
        def services_installed(patch):
            asg = ASG(patch.get('server_name'), self.env)
            status = asg.get_health()
            return status['is_healthy'] and status['instances_count'] == patch.get('scale_up_count')
        # Check if ASGs have installed all services
        ready_asgs = [ patch for patch in patches if services_installed(patch) ]
        for patch in ready_asgs:
            self.update_patch_status(patch, PatchStates.STATE_SERVICES_INSTALLED, False)
        self.write_to_file()

    def set_scale_in_size(self, patches):
        if not patches:
            return
        # Set scale in target size
        for patch in patches:
            size = patch.get('instances_count')
            max_size = patch.get('max_count')
            data = {'desired':size, 'max':max_size}
            asg_name = patch.get('server_name')
            update = self.api.put_asg_size(self.env, asg_name, data)
            self.update_patch_status(patch, PatchStates.STATE_SCALE_IN_TARGET_SET)

    def monitor_scale_in(self, patches):
        if not patches:
            return
        def has_scaled_in(patch):
            asg = ASG(patch.get('server_name'), self.env)
            status = asg.get_health()
            return status['is_healthy'] and status['instances_count'] == patch.get('instances_count')
        # Check if ASGs have finished scaling in
        scaled_in_asgs = [ patch for patch in patches if has_scaled_in(patch) ]
        for patch in scaled_in_asgs:
            self.update_patch_status(patch, PatchStates.STATE_COMPLETE, False)
        self.write_to_file()

    def update_patch_status(self, patch, status, write=True):
        patch['state'] = status
        patch['updated'] = str(datetime.datetime.utcnow())
        if write:
            self.write_to_file()

    def write_to_file(self):
        PatchFile.write_content(self.cluster, self.env, self.operation, self.is_refresh)



