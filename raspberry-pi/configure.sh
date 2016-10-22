#!/bin/sh
SCRIPT_DIR=$(cd $(dirname $0); pwd)
source=${SCRIPT_DIR}/conf/attendance.conf
dest=/etc/supervisor/conf.d/
cp ${source} ${dest}
