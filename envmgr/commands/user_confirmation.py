# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import os

from builtins import input
    
def confirm(message):
    if isinstance(message, list):
        message = os.linesep.join(message)
    confirm = input(message)
    return confirm.lower() == 'y'

