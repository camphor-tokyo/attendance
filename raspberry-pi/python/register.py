#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

from binascii import hexlify
from enum import Enum
import sys
import sqlite3

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


def register(idm, name):
    conn = sqlite3.connect(SQLITE_FILE)
    c = conn.cursor()

    try:
        # Check whether idm is already recorded or not
        c.execute("SELECT * FROM idms WHERE idm = '{}';".format(idm))
        is_recorded = (c.fetchone() is not None)
    except Exception as e:
        return SQLRESULT.ERROR, "error: {}".format(e)

    if is_recorded:
        # If idm is recorded, name will be updated
        sql = """
        UPDATE idms
        SET name='{}', modified=date('now')
        WHERE idm = '{}';
        """.format(name, idm)
        result = SQLRESULT.UPDATE
    else:
        # If idm is not recorded, (idm, name) will be inserted
        sql = """
        INSERT INTO idms (idm, name, created, modified)
        VALUES ('{}', '{}', date('now'), date('now'));
        """.format(idm, name)
        result = SQLRESULT.INSERT
    try:
        c.execute(sql)
        conn.commit()
    except Exception as e:
        return SQLRESULT.ERROR, "error: {}".format(e)

    conn.close()
    return result, None


def connected(tag):
    # idm の取得
    idm, err = extract_idm(tag)
    if err is not None:
        print(err)
        return
    print("Your IDm is {}".format(idm))

    # ユーザ名の取得
    print("Please input your slack account name: ", end="")
    sys.stdout.flush()
    name = sys.stdin.readline().rstrip()

    # idm とユーザ名の登録
    result, err = register(idm, name)
    if err is not None:
        print(err)
        return

    if result == SQLRESULT.INSERT:
        print("Your idm:{}, name:{} are registered!!".format(idm, name))
    else:
        print("Your idm:{}, name:{} are updated!!".format(idm, name))


if __name__ == "__main__":
    print("Please put your card on the nfc reader. Waiting...")
    sys.stdout.flush()
    clf = nfc.ContactlessFrontend('usb')
    clf.connect(rdwr={'on-connect': connected})
