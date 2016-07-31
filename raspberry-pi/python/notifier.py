#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

from enum import Enum
import sys
import sqlite3
import signal

import nfc

from common import extract_idm
from common import SQLITE_FILE, SQLITE_DATABASE, SQLRESULT


ATTEND = Enum('ARRIVED', 'LEFT', 'ERROR')

def notify(user, attend):
    if attend == ATTEND.ARRIVED:
        print("[NOTIFICATION] {} attends now".format(user))
    else:
        print("[NOTIFICATION] {} leaves now".format(user))
    return True, None


def write_attend_log(idm, attend):
    conn = sqlite3.connect(SQLITE_FILE)
    cur = conn.cursor()
    if attend is ATTEND.ARRIVED:
        result = SQLRESULT.INSERT
        sql = """
        INSERT INTO attend_logs (idm, arrived_time)
        VALUES ('{}', datetime('now'));
        """.format(idm)
    else:
        result = SQLRESULT.UPDATE
        sql = """
        UPDATE attend_logs
        SET left_time=datetime('now')
        WHERE idm = '{}'
              AND ARRIVED_TIME is not NULL
              AND LEFT_TIME is NULL
        """.format(idm)
    try:
         cur.execute(sql)
         conn.commit()
    except Exception as e:
        return SQLRESULT.ERROR, "[WARN] error: SQL failed because {}".format(e)
    conn.close()

    return result, None


def get_status_from_idm(idm):
    conn = sqlite3.connect(SQLITE_FILE)
    cur = conn.cursor()
    sql = """
    SELECT *
    FROM attend_logs
    WHERE idm = '{}'
          AND arrived_time is not NULL
          AND left_time is NULL
    """.format(idm)
    try:
         cur.execute(sql)
    except Exception as e:
        return ATTEND.ERROR, "[WARN] error: SQL failed because {}".format(e)
    row = cur.fetchone()
    conn.close()

    if row is None:
        result = ATTEND.ARRIVED
    else:
        result = ATTEND.LEFT

    return result, None


def get_user_from_idm(idm):
    conn = sqlite3.connect(SQLITE_FILE)
    cur = conn.cursor()
    sql = """
    SELECT name FROM idms WHERE idm = '{}'
    """.format(idm)
    try:
        cur.execute(sql)
    except Exception as e:
        return SQLRESULT.ERROR, "[WARN] error: SQL failed because {}".format(e)
    row = cur.fetchone()
    conn.close()

    if row is None:
        return SQLRESULT.ERROR, "[WARN] error: Failed to get user"
    else:
        user = row[0]
    return user, None


def released(tag):
    # idm の取得
    idm, err = extract_idm(tag)
    if err is not None:
        print(err)
        return
    print("[INFO] Your IDm is {}".format(idm))

    # idm から出席ログを取得する
    attend, err = get_status_from_idm(idm)
    if err is not None:
        print(err)
        return

    # attend_log に書き込みをする
    is_updated, err = write_attend_log(idm, attend)
    if err is not None:
        print(err)
        return

    # idm からユーザ名を取得する
    user, err = get_user_from_idm(idm)
    if err is not None:
        print(err)
        return

    # Notification を送る
    is_notified, err = notify(user, attend)
    if err is not None:
        print(err)
        return


def sigint_handler(*args):
    print("\n[INFO] Recieve SIGINT. Stop notifier.")
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    print("Please tap your card on the nfc reader. Waiting...")
    sys.stdout.flush()
    clf = nfc.ContactlessFrontend('usb')
    while True:
        clf.connect(rdwr={'on-release': released})
