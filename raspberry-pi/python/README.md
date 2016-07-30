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
