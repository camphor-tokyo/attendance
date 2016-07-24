#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

from binascii import hexlify
import sys

import nfc


def connected(tag):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            print("Your IDm is {}".format(hexlify(tag.idm).upper()))
        except Exception as e:
            print("error: {}".format(e))
    else:
        print("error: tag isn't Type3Tag")


if __name__ == "__main__":
    print("Please put your card on the nfc reader. Waiting...")
    sys.stdout.flush()
    clf = nfc.ContactlessFrontend('usb')
    clf.connect(rdwr={'on-connect': connected})

