# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import itertools
import sys
import time
import threading

class Spinner(object):
    spinner_cycle = itertools.cycle(['-', '\\', '|', '/'])

    def __init__(self):
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.init_spin)
        self.spin_thread.daemon = True

    def start(self):
        self.spin_thread.start()

    def stop(self):
        self.stop_running.set()
        self.spin_thread.join()
        sys.stdout.write('\r')
        sys.stdout.flush()
    
    def init_spin(self):
        while not self.stop_running.is_set():
            sys.stdout.write(next(self.spinner_cycle))
            sys.stdout.flush()
            time.sleep(0.2)
            sys.stdout.write('\b')

