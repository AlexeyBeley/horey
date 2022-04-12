#!/bin/bash
set -xe
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../../_venv/bin/activate
python provisioner.py --action move_file\
  --src_file_path "./STRING_REPLACEMENT_FILE_NAME.conf"\
  --dst_file_path "/etc/logrotate.d/STRING_REPLACEMENT_FILE_NAME.conf"