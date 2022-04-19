#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


logstash_pid=$(ps aux | grep 'logstash' | grep 'java' | awk '{print $2}')
if [ -n "${logstash_pid}" ]
then
      sudo kill -s 9 "${logstash_pid}"
else
      sudo systemctl restart logstash
fi
