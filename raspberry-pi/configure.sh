#!/bin/sh
SCRIPT_DIR=$(cd $(dirname $0); pwd)
source=${SCRIPT_DIR}/static/attendance.conf
dest=/etc/supervisor/conf.d/
cp ${source} ${dest}
