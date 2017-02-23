
import json
import os.path
import time

from envmgr.commands.asg import ASG
from progressbar import ProgressBar
from codecs import open
from hashlib import sha1
from appdirs import user_data_dir

class PatchProcess(object):

    SCALE_OUT = 'SCALE_OUT'
    WAIT_FOR_SCALE_OUT = 'WAIT_FOR_SCALE_OUT'
    SCALE_IN = 'SCALE_IN'
    WAIT_FOR_SCALE_IN = 'WAIT_FOR_SCALE_IN'

    total_progress = 0
    operation = {}

    def __init__(self, api):
        self.api = api
        self.app_dir = user_data_dir('envmgr', 'trainline')
        self.progress = ProgressBar(redirect_stdout=True)
        self.progress.update(0)

    def scale_out(self):
        env = self.operation.get('env')
        cluster = self.operation.get('cluster')
        patches = self.operation.get('patches')
        p = round((25 / len(patches) / 2)) 

        # Update Launch Configs
        for patch in patches:
            data = {'AMI':patch.get('new_ami_id')}
            asg_name = patch.get('server_name')
            update_lc = self.api.put_asg_launch_config(env, asg_name, data)
            self.total_progress += p
            self.progress.update(self.total_progress)

        # Set scale out target size
        for patch in patches:
            size = patch.get('scale_up_count')
            data = {'desired':size, 'max':size}
            asg_name = patch.get('server_name')
            update_size = self.api.put_asg_size(env, asg_name, data)
            self.total_progress += p
            self.progress.update(self.total_progress)

        self.operation['state'] = self.WAIT_FOR_SCALE_OUT
        self.write_patch_status(self.operation, cluster, env)
        self.wait_for_scale_out()

    def wait_for_scale_out(self):
        self.total_progress = 26
        self.progress.update(self.total_progress)
        env = self.operation.get('env')
        patches = self.operation.get('patches')
        np = len(patches)
        p = round(25 / np)

        def has_scaled_out(patch):
            asg = ASG({})
            status = asg.get_health(env, patch.get('server_name'))
            return status['is_healthy'] and status['instances_count'] == patch.get('scale_up_count')
        
        # Check all ASGS have scaled out and are fully running
        while True:
            scaled_out_asgs = [ patch for patch in patches if has_scaled_out(patch) ]
            n_complete = len(scaled_out_asgs)
            self.progress.update(self.total_progress + (p * n_complete))
            scale_out_complete = n_complete == np
            if scale_out_complete:
                print('Scale out complete')
                self.scale_in()
            else:
                time.sleep(30)

    def scale_in(self):
        self.total_progress = 51
        self.progress.update(self.total_progress)
        env = self.operation.get('env')
        cluster = self.operation.get('cluster')
        patches = self.operation.get('patches')
        p = round(25 / len(patches))

        # Set scale in target size
        for patch in patches:
            size = patch.get('instances_count')
            data = {'desired':size, 'max':size}
            asg_name = patch.get('server_name')
            update_size = self.api.put_asg_size(env, asg_name, data)
            self.total_progress += p
            self.progress.update(self.total_progress)

        self.operation['state'] = self.WAIT_FOR_SCALE_IN
        self.write_patch_status(self.operation, cluster, env)
        self.wait_for_scale_in()

    def wait_for_scale_in(self):
        self.total_progress = 76
        self.progress.update(self.total_progress)
        env = self.operation.get('env')
        cluster = self.operation.get('cluster')
        patches = self.operation.get('patches')
        np = len(patches)
        p = round(25 / np)
        
        def has_scaled_in(patch):
            asg = ASG({})
            status = asg.get_health(env, patch.get('server_name'))
            return status['is_healthy'] and status['instances_count'] == patch.get('instances_count')
        
        # Check all ASGS have scaled in and are fully running
        while True:
            scaled_in_asgs = [ patch for patch in patches if has_scaled_in(patch) ]
            n_complete = len(scaled_in_asgs)
            self.progress.update(self.total_progress + (p * n_complete))
            scale_in_complete = n_complete == np
            if scale_in_complete:
                self.progress.finish()
                print('Auto AMI patching is complete')
                os.remove(self.get_patch_file_path(cluster, env))
                return
            else:
                time.sleep(30)

    def process(self, patch_operation, cluster, env):
        self.operation = self.get_operation(patch_operation, cluster, env)
        state = self.operation.get('state')
        print('Patching {0} ASGS...'.format(len(self.operation.get('patches'))))

        if state is None:
            self.scale_out()
        elif state == self.WAIT_FOR_SCALE_OUT:
            self.wait_for_scale_out()
        elif state == self.WAIT_FOR_SCALE_IN:
            self.wait_for_scale_in()
        else:
            print('Unknown state')

    def get_operation(self, patch_item, cluster, env):
        if isinstance(patch_item, list):
            return {
                'patches': patch_item,
                'cluster': cluster,
                'env': env
                }
        else:
            return patch_item
    
    def write_patch_status(self, operation, cluster, env):
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
