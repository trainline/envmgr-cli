# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time
import datetime

from progressbar import ProgressBar, FormatLabel, Timer, Bar, RotatingMarker, Percentage
from envmgr.commands.patching.patch_process import PatchProcess
from envmgr.commands.patching.patch_states import PatchStates
from envmgr.commands.patching.patch_file import PatchFile
from envmgr.commands.patching.patch_progress import PatchProgress
from envmgr.commands.patch_table import patch_table
from builtins import input

class PatchOperation(object):
    proc = None
    operation = {}
    
    def __init__(self, api):
        self.api = api

    def get_patches_by_state(self, state):
        patches = self.operation.get('patches', [])
        return [ patch for patch in patches if patch.get('state') == state ]

    def run(self, patch_operation, cluster, env):
        self.operation = self.get_operation(patch_operation, cluster, env)
        self.proc = PatchProcess(self.api, self.operation)
        self.progress = PatchProgress()
        self.progress.start()
        self.check_status()

    def check_status(self):
        while True:            
            patches = self.operation.get('patches')

            update_lc = self.get_patches_by_state(None)
            set_scale_out = self.get_patches_by_state(PatchStates.STATE_LC_UPDATED)
            scaling_out = self.get_patches_by_state(PatchStates.STATE_SCALE_OUT_TARGET_SET)
            set_scale_in = self.get_patches_by_state(PatchStates.STATE_SCALED_OUT)
            scaling_in = self.get_patches_by_state(PatchStates.STATE_SCALE_IN_TARGET_SET)
            complete = self.get_patches_by_state(PatchStates.STATE_COMPLETE)

            self.progress.update(*map(len, [patches, set_scale_out, scaling_out, set_scale_in, scaling_in, complete]))
            self.proc.update_launch_configs(update_lc)
            self.proc.set_scale_out_size(set_scale_out)
            self.proc.monitor_scale_out(scaling_out)
            self.proc.set_scale_in_size(set_scale_in)
            self.proc.monitor_scale_in(scaling_in)
            
            all_complete = all([ patch.get('state') == PatchStates.STATE_COMPLETE for patch in patches ])
            if all_complete:
                self.update_progress()
                self.progress.finish()
                PatchFile.delete(self.operation.get('cluster'), self.operation.get('env'))
                return
            else:
                time.sleep(10)

    def get_report(self, cluster, env):
        current_operation = self.get_existing(cluster, env)
        if current_operation is None:
            print('No pending patch operation found for {0} in {1}'.format(cluster, env))
        else:
            patches = current_operation.get('patches')
            table_data = patch_table(patches, PatchStates.get_friendly_name)
            print(table_data)
            
    def kill_current(self, cluster, env):
        current_operation = self.get_existing(cluster, env)
        if current_operation is None:
            print('No pending patch operation found for {0} in {1}'.format(cluster, env))
        else:
            confirm = input('Are you sure you want to kill this process? (y/n) ')
            if confirm.lower() == 'y':
                # self.remove_patch_file(cluster, env)
                print('Confirmed')
            else:
                print('Aborted')
    
    def get_operation(self, patch_item, cluster, env):
        if isinstance(patch_item, list):
            return {'patches':patch_item, 'cluster':cluster, 'env':env, 'start':str(datetime.datetime.utcnow())}
        else:
            return patch_item

    def get_existing(self, cluster, env):
        return PatchFile.get_contents(cluster, env)


