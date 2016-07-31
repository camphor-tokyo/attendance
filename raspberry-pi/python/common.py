#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

from binascii import hexlify
from enum import Enum

import nfc

SQLITE_FILE = "attendance.db"
SQLITE_DATABASE = "tokyo"
SQLRESULT = Enum('INSERT', 'UPDATE', 'ERROR')


def extract_idm(tag):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            return hexlify(tag.idm).upper(), None
        except Exception as e:
            return None, "error: {}".format(e)
    return None,"error: tag isn't Type3Tag"
