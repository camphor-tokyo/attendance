#!/usr/bin/env python
# coding:utf-8
from __future__ import print_function

import signal
import time

from attendance import Attendance


def sigint_handler(self, *args):
    print("\n[INFO] Recieve SIGINT. Stop notifier.")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    attendance = Attendance()
    attendance.daemon = True
    attendance.start()

    # keep main thread alive
    while True:
        time.sleep(1)
