**DEMO用データベースの準備 (sql)**
```bash
$ sqlite3 attendance.db < migrate.sql
```

**DEMO用の python の準備**
```bash
$ virtualenv -p /usr/local/opt/python/bin/python2.7 venv
$ source venv venv/bin/activate
$ pip install -r requirements.txt
```

**IDM取得のデモ**
```bash
$ source venv/bin/activate
$ python test.py
```

```
(venv) ➜  python git:(1-nfc_python_client) ✗ python test.py
> Please put your card on the nfc reader. Waiting...
> Your IDm is xxxxxxxxxx
```

**登録のデモ**

```bash
$ source venv/bin/activate
$ python register.py
```

```bash
(venv) ➜  python git:(1-nfc_python_client) ✗ python register.py
> Please put your card on the nfc reader. Waiting...
> Your IDm is xxxxxxxxxx
> Please input your slack account name: shotarok
> Your idm:012E34D4B64A295A, name:shotarok are registered!!
(venv) ➜  python git:(1-nfc_python_client) ✗ python register.py
> Please put your card on the nfc reader. Waiting...
> Your IDm is 012E34D4B64A295A
> Please input your slack account name: kohama
> Your idm:xxxxxxxxxx, name:kohama are updated!!
```

**通知のデモ**

```bash
$ source venv/bin/activate
$ python notifier.py
```

```bash
Your idm:012E34D4B64A295A, name:@shotarok are registered!!
(venv) ➜  python git:(1-notifier) ✗ python notifier.py
Please tap your card on the nfc reader. Waiting...
[INFO] Your IDm is 012E34D4B64A295A
[NOTIFICATION] @shotarok attends now
[INFO] Your IDm is 012E34D4B64A295A
[NOTIFICATION] @shotarok leaves now
[INFO] Your IDm is 012E34D4B64A295A
[NOTIFICATION] @shotarok attends now
[INFO] Your IDm is 012E34D4B64A295A
[NOTIFICATION] @shotarok leaves now
^C
[INFO] Recieve SIGINT. Stop notifier.
(venv) ➜  python git:(1-notifier) ✗ sqlite3 attendance.db
SQLite version 3.8.10.2 2015-05-20 18:17:19
Enter ".help" for usage hints.
sqlite> select * from attend_logs;
1|012E34D4B64A295A|2016-07-31 01:50:49|2016-07-31 01:50:51
2|012E34D4B64A295A|2016-07-31 01:50:53|2016-07-31 01:50:55
sqlite> ^D
```
