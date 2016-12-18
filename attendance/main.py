#!/usr/bin/env python
# coding:utf-8
from __future__ import print_function

import signal
import time

import RPi.GPIO as GPIO
from attendance import Attendance


def sigint_handler(self, *args):
    print("\n[INFO] Recieve SIGINT. Stop notifier.")
    GPIO.cleanup()
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    attendance = Attendance()
    attendance.mode = attendance.MODE.ATTEND
    attendance.daemon = True
    attendance.start()

    SWITCH_PIN = 2
    RED_LED_PIN = 3
    GREEN_LED_PIN = 4
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)

    last_pin_status = 0
    while True:
        pin_status = GPIO.input(SWITCH_PIN)
        if last_pin_status == 1 and pin_status == 0:
            attendance.toggle_mode()
        last_pin_status = pin_status

        if attendance.mode == Attendance.MODE.ATTEND:
            GPIO.output(RED_LED_PIN, False)
            GPIO.output(GREEN_LED_PIN, True)
        elif attendance.mode == Attendance.MODE.REGISTER:
            GPIO.output(RED_LED_PIN, True)
            GPIO.output(GREEN_LED_PIN, False)

        time.sleep(0.1)
