#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../../_venv/bin/activate
python provisioner.py --action check_file_contains\
  --src_file_path STRING_REPLACEMENT_FILTER_FILE_NAME\
  --dst_file_path "/etc/logstash/conf.d/STRING_REPLACEMENT_PIPELINE_NAME.conf"\
