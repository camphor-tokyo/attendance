FROM python:2.7

ENV app /app
RUN mkdir $app
WORKDIR $app
ADD . $app

RUN apt-get update && \
    apt-get install -y sqlite3 libusb-1.0-0-dev
RUN sqlite3 attendance.db < migrate.sql
RUN pip install -r requirements.txt

CMD python attendance.py
