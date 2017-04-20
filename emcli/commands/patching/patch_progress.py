# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

import time
import sys
import threading
import math
import datetime
import progressbar.utils

from progressbar import ProgressBar, FormatLabel, Timer, Bar, RotatingMarker, Percentage

class PatchProgress(object):
    widgets = []
    total_progress = 0
    start_time = 0

    def __init__(self):
        self.stop_running = threading.Event()
        self.progress_thread = threading.Thread(target=self.init_progress)
        self.progress_thread.daemon = True
        spinner = RotatingMarker()
        spinner.INTERVAL = datetime.timedelta(milliseconds=100)
        self.widgets = [spinner, ' ', Percentage(), ' ', FormatLabel('Calculating patch requirements'), ' ', Bar(), ' ', FormatLabel('')]
        self.progress = ProgressBar(redirect_stdout=True, widgets=self.widgets, max_value=100)
        self.progress.update(0)

    def update(self, n_total, n_lc_updated, n_scaling_out, n_scaled_out, n_services_installed, n_scaling_in, n_complete, *args):
        msg = '[Patching {0} ASGs]: '.format(n_total)
        stages = []
        if n_lc_updated is not 0:
            stages.append('{0} Launch Configs Updated'.format(n_lc_updated))
        if n_scaling_out is not 0:
            stages.append('{0} Scaling Out'.format(n_scaling_out))
        if n_scaled_out is not 0:
            stages.append('{0} Installing Services'.format(n_scaled_out))
        if n_scaling_in is not 0:
            stages.append('{0} Scaling In'.format(n_scaling_in))
        if n_complete is not 0:
            stages.append('{0} Complete'.format(n_complete))
        msg += ', '.join(stages)
        self.widgets[4] = FormatLabel(msg)
        t1 = (5 / n_total) * n_lc_updated
        t2 = (10 / n_total) * n_scaling_out
        t3 = (30 / n_total) * n_scaled_out
        t4 = (70 / n_total) * n_services_installed
        t5 = (75 / n_total) * n_scaling_in
        t6 = (100 / n_total) * n_complete
        self.total_progress = t1 + t2 + t3 + t4 + t5 + t6

    def start(self, time):
        self.start_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        self.progress_thread.start()

    def stop(self):
        self.stop_running.set()
        self.progress_thread.join()

    def finish(self, total):
        msg = '[Patching {0} ASGs]: {0} Complete'.format(total)
        self.widgets[4] = FormatLabel(msg)
        self.progress.finish()

    def init_progress(self):
        while not self.stop_running.is_set():
            p = self.total_progress
            if math.isnan(p) or p is None or p == 0:
                p = 1
            t = datetime.datetime.utcnow()
            s = (t - self.start_time).total_seconds()
            elapsed = progressbar.utils.format_time(s)
            self.widgets[8] = FormatLabel('Elapsed Time: {0}'.format(elapsed))
            self.progress.update(p)
            time.sleep(0.2)

