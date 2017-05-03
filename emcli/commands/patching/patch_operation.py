# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
import time
import datetime

from progressbar import ProgressBar, FormatLabel, Timer, Bar, RotatingMarker, Percentage
from emcli.commands.patching.patch_process import PatchProcess
from emcli.commands.patching.patch_states import PatchStates
from emcli.commands.patching.patch_file import PatchFile
from emcli.commands.patching.patch_progress import PatchProgress
from emcli.commands.patching.patch_table import patch_table
from emcli.commands.user_confirmation import confirm

from builtins import input

class PatchOperation(object):
    
    proc = None
    operation = {}
    is_refresh = False

    @staticmethod
    def get_current_status(cluster, env, is_refresh=False):
        current_operation = PatchOperation.get_current(cluster, env, is_refresh)
        if current_operation is not None:
            patches = current_operation.get('patches')
            return patch_table(patches, PatchStates.get_friendly_name)
    
    @staticmethod
    def is_in_progress(cluster, env, is_refresh=False):
        return PatchOperation.get_current(cluster, env, is_refresh) is not None

    @staticmethod
    def get_current(cluster, env, is_refresh=False):
        return PatchFile.get_contents(cluster, env, is_refresh)
    
    @staticmethod
    def get_patches_by_availability(patches, available):
        if available:
            return [ patch for patch in patches if not patch.get('has_standby_instances') and not patch.get('unhealthy') and not patch.get('invalid_ami')]
        else:
            return [ patch for patch in patches if patch.get('has_standby_instances') or patch.get('unhealthy') or patch.get('invalid_ami')]

    @staticmethod
    def describe_patches(to_run, to_ignore=None):
        description = ['']
        if to_run:
            description.extend(('The following patch operations are required:', patch_table(to_run), ''))
        if to_ignore:
            description.extend(('The following patches cannot be run at this time and will be ignored:', patch_table(to_ignore), ''))
        return description

    @staticmethod
    def kill(cluster, env, is_refresh=False):
        if not PatchOperation.is_in_progress(cluster, env, is_refresh):
            print('No pending patch operation found for {0} in {1}'.format(cluster, env))
        else:
            message = ['', 'This will kill the current patch operation:']
            message.append(PatchOperation.get_current_status(cluster, env, is_refresh))
            message.extend(('Scale in/out operations currently in progress will not be affected.', ''))
            message.append('Are you sure you want to kill this operation? (y/n) ')
            if confirm(message):
                report = PatchFile.write_report(cluster, env, is_refresh)
                PatchFile.delete(cluster, env, is_refresh)
                print('Patch operation deleted. Status report written to {0}'.format(report))
    
    def __init__(self, api):
        self.api = api

    def get_patches_by_state(self, state):
        patches = self.operation.get('patches', [])
        return [ patch for patch in patches if patch.get('state') == state ]

    def run(self, patch_operation, cluster, env, is_refresh=False):
        PatchOperation.is_refresh = is_refresh
        self.operation = self.get_operation(patch_operation, cluster, env)
        self.proc = PatchProcess(self.api, self.operation, is_refresh)
        self.progress = PatchProgress()
        self.progress.start(self.operation.get('start'))
        self.check_status()

    def check_status(self):
        while True:            
            patches = self.operation.get('patches')

            update_lc = self.get_patches_by_state(None)
            set_scale_out = self.get_patches_by_state(PatchStates.STATE_LC_UPDATED)
            scaling_out = self.get_patches_by_state(PatchStates.STATE_SCALE_OUT_TARGET_SET)
            installing_services = self.get_patches_by_state(PatchStates.STATE_SCALED_OUT)
            set_scale_in = self.get_patches_by_state(PatchStates.STATE_SERVICES_INSTALLED)
            scaling_in = self.get_patches_by_state(PatchStates.STATE_SCALE_IN_TARGET_SET)
            complete = self.get_patches_by_state(PatchStates.STATE_COMPLETE)

            self.progress.update(*map(len, [patches, set_scale_out, scaling_out, installing_services, set_scale_in, scaling_in, complete]))
            self.proc.update_launch_configs(update_lc)
            self.proc.set_scale_out_size(set_scale_out)
            self.proc.monitor_scale_out(scaling_out)
            self.proc.monitor_service_installation(installing_services)
            self.proc.set_scale_in_size(set_scale_in)
            self.proc.monitor_scale_in(scaling_in)
            
            if all([ patch.get('state') == PatchStates.STATE_COMPLETE for patch in patches ]):
                self.progress.finish(len(patches))
                PatchFile.delete(self.operation.get('cluster'), self.operation.get('env'), PatchOperation.is_refresh)
                return
            else:
                time.sleep(10)        
    
    def get_operation(self, patch_item, cluster, env):
        if isinstance(patch_item, list):
            patches = PatchOperation.get_patches_by_availability(patch_item, True)
            return {'patches':patches, 'cluster':cluster, 'env':env, 'start':str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"))}
        else:
            return patch_item

