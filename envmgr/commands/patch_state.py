
import json
import os.path

from codecs import open
from hashlib import sha1
from appdirs import user_data_dir

class PatchState(object):

    SCALE_OUT = 'SCALE_OUT'
    WAIT_FOR_SCALE_OUT = 'WAIT_FOR_SCALE_OUT'
    SCALE_IN = 'SCALE_IN'
    WAIT_FOR_SCALE_IN = 'WAIT_FOR_SCALE_IN'

    cluster = None
    env = None
    patches = []

    def __init__(self, api):
        self.api = api
        self.app_dir = user_data_dir('envmgr', 'trainline')

    def scale_out(self):
        print('Set scale out state ')
        print('Write patch file')
        print('Update launch configs for each ASG in patch')
        print('Set desired size of each ASG')
        self.wait_for_scale_out()

    def wait_for_scale_out(self):
        print('Waiting for scale out')
        self.scale_in()

    def scale_in(self):
        print('Set scale in state')
        print('Write patch file')
        print('Set desired size of ASG to original')
        self.wait_for_scale_in()

    def wait_for_scale_in(self):
        print('Waiting for scale in')

    def get_state(self, cluster, env):
        patch = self.get_patch_if_exists(cluster, env)
        if patch is None:
            self.scale_out()
        else:
            state = patch.get('state')
            if state == self.WAIT_FOR_SCALE_OUT:
                self.wait_for_scale_out()
            elif state == self.WAIT_FOR_SCALE_IN:
                self.wait_for_scale_in()
            else:
                print('Unknown state')

    

    def get_patch_if_exists(self, cluster, env):
        filename = 'patch_{0}_{1}'.format(cluster.lower(), env.lower())
        filename = '{0}.json'.format(sha1(filename).hexdigest())
        abs_path = os.path.join(self.app_dir, filename)
        if os.path.exists(abs_path):
            with open(abs_path, encoding='utf-8') as file_data:
                return json.load(file_data)
        else:
            return None
