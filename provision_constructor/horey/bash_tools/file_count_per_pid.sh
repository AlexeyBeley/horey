#!/bin/bash

set +e

pid_list=$(sudo ps -aux | awk '{ print $2 }' | tail -n +2)


for COUNTER in $pid_list
do
 file_count=$(sudo lsof -p "${COUNTER}" |wc -l)
 echo "${COUNTER}: ${file_count}"
done
