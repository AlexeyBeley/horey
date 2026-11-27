#!/bin/bash

set -xe

# ./run_remote.sh script_path host_base_name last_counter
# ./run_remote.sh "resize_aws_volume.sh" "production-host-" 1

script_path=$1
host_base_name=$2
last_counter=$3

script_name=$(basename ${script_path})

for COUNTER in $(seq 0 1 "$last_counter")
do
  scp "${script_path}" "${host_base_name}${COUNTER}:/tmp/adhoc.sh"
  ssh "${host_base_name}${COUNTER}" << 'ENDSSH'
  hostname=$(cat /etc/hostname)
  echo ${hostname}
  sudo chmod +x /tmp/adhoc.sh
  /tmp/adhoc.sh
ENDSSH

done
