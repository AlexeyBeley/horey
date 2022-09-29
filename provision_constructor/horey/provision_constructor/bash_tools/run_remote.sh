#!/bin/bash

set -xe

# run_remote.sh script_path host_base_name last_counter
# tail -n +1 output_*.txt
script_path=$1
host_base_name=$2
last_counter=$3

mkdir -p "./adhoc_outputs"
rm -f ./adhoc_outputs/output_*

for COUNTER in $(seq 0 1 "$last_counter")
do
  scp "${script_path}" "${host_base_name}${COUNTER}:/tmp/adhoc.sh"
  ssh "${host_base_name}${COUNTER}" << 'ENDSSH'
  hostname=$(cat /etc/hostname)
  echo ${hostname}
  sudo chmod +x /tmp/adhoc.sh
  /tmp/adhoc.sh > "/tmp/adhoc_output.txt"
ENDSSH
scp "${host_base_name}${COUNTER}:/tmp/adhoc_output.txt" "./adhoc_outputs/output_${COUNTER}.txt"
done
