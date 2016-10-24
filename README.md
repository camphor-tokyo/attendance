# attendance
CAMPHOR- Tokyo 出席簿

## How to run on Raspberry Pi
### Setup
```sh
apt-get update
apt-get install -y sqlite3 libusb-1.0-0-dev

cd raspberry-pi/python
sqlite3 attendance.db < migrate.sql
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start
Start `attendance.py` with supervisord

```sh
cd raspberry-pi
sudo supervisord -c supervisord.conf
```