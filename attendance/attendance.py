#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

import json
import os
import sqlite3
import sys
import threading
import urllib
import urllib2
from enum import Enum

import nfc

from common import SQLITE_DATABASE, SQLITE_FILE, SQLRESULT, extract_idm


class Attendance(threading.Thread):
    ATTEND = Enum('ARRIVED', 'LEFT', 'ERROR')

    def __init__(self):
        super(Attendance, self).__init__()

    def run(self):
        print("Please tap your card on the nfc reader. Waiting...")
        sys.stdout.flush()
        clf = nfc.ContactlessFrontend('usb')
        while True:
            clf.connect(rdwr={'on-release': self.released})

    def notify(self, user, attend):
        if attend == self.ATTEND.ARRIVED:
            print("[NOTIFICATION] {} attends now".format(user))
            self.notify_to_slack(text="{} が来ました".format(user))
        elif attend == self.ATTEND.LEFT:
            print("[NOTIFICATION] {} leaves now".format(user))
            self.notify_to_slack(text="{} が帰りました".format(user))
        else:
            return False, "[WARN] error: attend should be ARRIVED or LEFT"
        return True, None

    def write_attend_log(self, idm, attend):
        conn = sqlite3.connect(SQLITE_FILE)
        cur = conn.cursor()
        if attend == self.ATTEND.ARRIVED:
            result = SQLRESULT.INSERT
            sql = """
            INSERT INTO attend_logs (idm, arrived_time)
            VALUES ('{}', datetime('now'));
            """.format(idm)
        elif attend == self.ATTEND.LEFT:
            result = SQLRESULT.UPDATE
            sql = """
            UPDATE attend_logs
            SET left_time=datetime('now')
            WHERE idm = '{}'
                  AND ARRIVED_TIME is not NULL
                  AND LEFT_TIME is NULL
            """.format(idm)
        else:
            return SQLRESULT.ERROR, "[WARN] error: attend should be ARRIVED or LEFT"
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            return SQLRESULT.ERROR, "[WARN] error: SQL failed because {}".format(e)
        conn.close()

        return result, None

    def get_status_from_idm(self, idm):
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
            return self.ATTEND.ERROR, "[WARN] error: SQL failed because {}".format(e)
        row = cur.fetchone()
        conn.close()

        if row is None:
            result = self.ATTEND.ARRIVED
        else:
            result = self.ATTEND.LEFT

        return result, None

    def get_user_from_idm(self, idm):
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

    def released(self, tag):
        # idm の取得
        idm, err = extract_idm(tag)
        if err is not None:
            print(err)
            return
        print("[INFO] Your IDm is {}".format(idm))

        # idm から出席ログを取得する
        attend, err = self.get_status_from_idm(idm)
        if err is not None:
            print(err)
            return

        # attend_log に書き込みをする
        is_updated, err = self.write_attend_log(idm, attend)
        if err is not None:
            print(err)
            return

        # idm からユーザ名を取得する
        user, err = self.get_user_from_idm(idm)
        if err is not None:
            print(err)
            return

        # @ から始まっていない場合は先頭に @ をつける
        if not user.startswith("@"):
            user = "@" + user

        # Notification を送る
        is_notified, err = self.notify(user, attend)
        if err is not None:
            print(err)
            return

    def notify_to_slack(self, text, channel=None, username=None, icon_emoji=None):
        url = os.environ["SLACK_WEBHOOK_URL"]
        if url is None:
            return

        payload = {
            "text": text,
            "channel": channel,
            "username": username,
            "icon_emoji": icon_emoji,
            "link_names": 1
        }
        payload_json = json.dumps(payload)
        data = urllib.urlencode({"payload": payload_json})
        request = urllib2.Request(url, data)
        urllib2.urlopen(request)
