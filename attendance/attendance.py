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
    MODE = Enum('ATTEND', 'REGISTER')
    ATTEND = Enum('ARRIVED', 'LEFT', 'ERROR')

    def __init__(self):
        super(Attendance, self).__init__()
        self.mode = self.MODE.ATTEND

    def run(self):
        print("Please tap your card on the nfc reader. Waiting...")
        sys.stdout.flush()
        clf = nfc.ContactlessFrontend('usb')
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

    def register(self, idm, name):
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

    def released(self, tag):
        if self.mode == self.MODE.ATTEND:
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
        elif self.mode == self.MODE.REGISTER:
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
            result, err = self.register(idm, name)
            if err is not None:
                print(err)
                return

            if result == SQLRESULT.INSERT:
                print("Your idm:{}, name:{} are registered!!".format(idm, name))
            else:
                print("Your idm:{}, name:{} are updated!!".format(idm, name))

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
