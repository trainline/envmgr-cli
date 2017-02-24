
import json
import os.path
import time
import datetime

from progressbar import ProgressBar, FormatLabel, Timer, Bar, RotatingMarker, Percentage
from envmgr.commands.asg import ASG
from codecs import open
from hashlib import sha1
from appdirs import user_data_dir

class PatchProcess(object):

    STATE_LC_UPDATED = 'launch_config_updated'
    STATE_SCALE_OUT_TARGET_SET = 'scale_out_target_set'
    STATE_SCALED_OUT = 'scale_out_complete'
    STATE_SCALE_IN_TARGET_SET = 'scale_in_target_set'
    STATE_COMPLETE = 'complete'

    operation = {}
    widgets = []
    total_progress = 0
    
    def __init__(self, api):
        self.api = api
        self.app_dir = user_data_dir('envmgr', 'trainline')
        self.widgets = [RotatingMarker(), ' ', Percentage(), ' ', FormatLabel('Calculating patch requirements'), ' ', Bar(), ' ', Timer()]
        self.progress = ProgressBar(redirect_stdout=True, widgets=self.widgets)
        self.progress.update(0)

    def update_progress(self):
        patches = self.operation.get('patches')
        n_total = len(patches)
        n_lc_updated = len(self.get_patches_by_status(self.STATE_LC_UPDATED))
        n_scaling_out = len(self.get_patches_by_status(self.STATE_SCALE_OUT_TARGET_SET))
        n_scaled_out = len(self.get_patches_by_status(self.STATE_SCALED_OUT))
        n_scaling_in = len(self.get_patches_by_status(self.STATE_SCALE_IN_TARGET_SET))
        n_complete = len(self.get_patches_by_status(self.STATE_COMPLETE))
        msg = '[Patching {0} ASGs]: {1} Scaling out, {2} Scaling in, {3} Complete'.format(
                n_total, n_scaling_out, n_scaling_in, n_complete)
        self.widgets[4] = FormatLabel(msg)
    
        t1 = (5 / n_total) * n_lc_updated
        t2 = (10 / n_total) * n_scaling_out
        t3 = (50 / n_total) * n_scaled_out
        t4 = (60 / n_total) * n_scaling_in
        t5 = (100 / n_total) * n_complete
        self.progress.update(t1 + t2 + t3 + t4 + t5)

    def get_patches_by_status(self, status):
        patches = self.operation.get('patches', [])
        return [ patch for patch in patches if patch.get('state') == status ]

    def update_launch_configs(self, patches):
        if not patches:
            return

        env = self.operation.get('env')
        cluster = self.operation.get('cluster')
        # Update Launch Configs
        for patch in patches:
            asg_name = patch.get('server_name')
            data = {'AMI':patch.get('new_ami_id')}
            update = self.api.put_asg_launch_config(env, asg_name, data)
            self.update_patch_status(patch, self.STATE_LC_UPDATED)
        
    def set_scale_out_size(self, patches):
        if not patches:
            return

        env = self.operation.get('env')
        cluster = self.operation.get('cluster')
        # Set scale out target size
        for patch in patches:
            size = patch.get('scale_up_count')
            asg_name = patch.get('server_name')
            data = {'desired':size, 'max':size}
            update = self.api.put_asg_size(env, asg_name, data)
            self.update_patch_status(patch, self.STATE_SCALE_OUT_TARGET_SET)

    def monitor_scale_out(self, patches):
        if not patches:
            return

        env = self.operation.get('env')
        def has_scaled_out(patch):
            asg = ASG({})
            status = asg.get_health(env, patch.get('server_name'))
            return status['is_healthy'] and status['instances_count'] == patch.get('scale_up_count')
        # Check if ASGs have finished scaling out 
        scaled_out_asgs = [ patch for patch in patches if has_scaled_out(patch) ]
        for patch in scaled_out_asgs:
            self.update_patch_status(patch, self.STATE_SCALED_OUT, False)
        self.write_patch_status()

    def set_scale_in_size(self, patches):
        if not patches:
            return
        
        env = self.operation.get('env')
        cluster = self.operation.get('cluster')
        # Set scale in target size
        for patch in patches:
            size = patch.get('instances_count')
            data = {'desired':size, 'max':size}
            asg_name = patch.get('server_name')
            update = self.api.put_asg_size(env, asg_name, data)
            self.update_patch_status(patch, self.STATE_SCALE_IN_TARGET_SET)

    def monitor_scale_in(self, patches):
        if not patches:
            return

        env = self.operation.get('env')
        def has_scaled_in(patch):
            asg = ASG({})
            status = asg.get_health(env, patch.get('server_name'))
            return status['is_healthy'] and status['instances_count'] == patch.get('instances_count')
        # Check if ASGs have finished scaling in
        scaled_in_asgs = [ patch for patch in patches if has_scaled_in(patch) ]
        for patch in scaled_in_asgs:
            self.update_patch_status(patch, self.STATE_COMPLETE, False)

    def process(self, patch_operation, cluster, env):
        self.operation = self.get_operation(patch_operation, cluster, env)
        self.check_status()

    def check_status(self):
        while True:
            self.update_progress()
            self.update_launch_configs(
                    self.get_patches_by_status(None))
            self.set_scale_out_size(
                    self.get_patches_by_status(self.STATE_LC_UPDATED))
            self.monitor_scale_out(
                    self.get_patches_by_status(self.STATE_SCALE_OUT_TARGET_SET))
            self.set_scale_in_size(
                    self.get_patches_by_status(self.STATE_SCALED_OUT))
            self.monitor_scale_in(
                    self.get_patches_by_status(self.STATE_SCALE_IN_TARGET_SET))
            
            patches = self.operation.get('patches')
            all_complete = all([ patch.get('state') == self.STATE_COMPLETE for patch in patches ])
            if all_complete:
                self.update_progress()
                self.progress.finish()
                os.remove(self.get_patch_file_path(self.operation.get('cluster'), self.operation.get('env')))
                return
            else:
                time.sleep(10)

    def get_operation(self, patch_item, cluster, env):
        if isinstance(patch_item, list):
            return {
                'patches': patch_item,
                'cluster': cluster,
                'env': env,
                'start': str(datetime.datetime.utcnow())
                }
        else:
            return patch_item
    
    def update_patch_status(self, patch, status, write=True):
        patch['state'] = status
        if write:
            self.write_patch_status()
    
    def write_patch_status(self):
        operation = self.operation
        cluster = operation.get('cluster')
        env = operation.get('env')
        patch_file = self.get_patch_file_path(cluster, env)
        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(operation, ensure_ascii=False)))

    def get_patch_file_path(self, cluster, env):
        filename = 'patch_{0}_{1}'.format(cluster.lower(), env.lower())
        filename = '{0}.json'.format(sha1(filename).hexdigest())
        return os.path.join(self.app_dir, filename)

    def get_existing(self, cluster, env):
        patch_file = self.get_patch_file_path(cluster, env)
        if os.path.exists(patch_file):
            with open(patch_file, encoding='utf-8') as file_data:
                return json.load(file_data)
        else:
            return None
