# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os
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
    
    @staticmethod
    def get_current_status(cluster, env):
        current_operation = PatchOperation.get_current(cluster, env)
        if current_operation is not None:
            patches = current_operation.get('patches')
            return patch_table(patches, PatchStates.get_friendly_name)
    
    @staticmethod
    def is_in_progress(cluster, env):
        return PatchOperation.get_current(cluster, env) is not None

    @staticmethod
    def get_current(cluster, env):
        return PatchFile.get_contents(cluster, env)
    
    @staticmethod
    def kill(cluster, env):
        if not PatchOperation.is_in_progress(cluster, env):
            print('No pending patch operation found for {0} in {1}'.format(cluster, env))
        else:
            message = ['', 'This will kill the current patch operation:']
            message.append(PatchOperation.get_current_status(cluster, env))
            message.extend(('Scale in/out operations currently in progress will not be affected.', ''))
            message.append('Are you sure you want to kill this operation? (y/n) ')
            confirm = input(os.linesep.join(message))
            if confirm.lower() == 'y':
                PatchFile.delete(cluster, env)
                print('Patch operation deleted')
    
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
            
            if all([ patch.get('state') == PatchStates.STATE_COMPLETE for patch in patches ]):
                self.update_progress()
                self.progress.finish()
                PatchFile.delete(self.operation.get('cluster'), self.operation.get('env'))
                return
            else:
                time.sleep(10)        
    
    def get_operation(self, patch_item, cluster, env):
        if isinstance(patch_item, list):
            return {'patches':patch_item, 'cluster':cluster, 'env':env, 'start':str(datetime.datetime.utcnow())}
        else:
            return patch_item

