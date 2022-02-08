#!/bin/bash

set -xe

TEMPLATE=$1
COUNT=$2
SCRIPT_PATH=$3

for COUNTER in 0 1 2 3 4 5 6 7 8 9 10 11 12 13
do
  ssh x-${COUNTER} << 'ENDSSH'
  hostname=$(cat /etc/hostname)
  echo ${hostname}
  cat /var/log/x.log | grep "ERROR"  >> /tmp/x_${hostname}.log
ENDSSH
done


for COUNTER in 0 1 2 3 4 5 6 7 8 9 10 11 12 13
do
  scp x-${COUNTER}:/tmp/x_*.log /tmp/
done