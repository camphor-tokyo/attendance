# attendance
CAMPHOR- Tokyo 出席簿

## How to run on Raspberry Pi
### Setup
```sh
apt-get update
apt-get install -y sqlite3 libusb-1.0-0-dev

cd attendance
sqlite3 attendance.db < migrate.sql
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start
```sh
cd attendance
source venv/bin/activate
SLACK_WEBHOOK_URL=<YOUR_SLACK_WEBHOOK_URL> python main.py
```
