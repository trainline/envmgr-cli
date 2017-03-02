# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

# Simple Enum for Py 2 & 3
class PatchStates:
    STATE_LC_UPDATED = 'launch_config_updated'
    STATE_SCALE_OUT_TARGET_SET = 'scale_out_target_set'
    STATE_SCALED_OUT = 'scale_out_complete'
    STATE_SCALE_IN_TARGET_SET = 'scale_in_target_set'
    STATE_COMPLETE = 'complete'

    @staticmethod
    def get_friendly_name(from_patch):
        friendly_names = {
            None: 'Updating Launch Config',
            PatchStates.STATE_LC_UPDATED: 'Setting scale out size',
            PatchStates.STATE_SCALE_OUT_TARGET_SET: 'Scaling out',
            PatchStates.STATE_SCALED_OUT: 'Setting scale in size',
            PatchStates.STATE_SCALE_IN_TARGET_SET: 'Scaling in',
            PatchStates.STATE_COMPLETE: 'Complete'
        }
        return friendly_names.get(from_patch.get('state'))

