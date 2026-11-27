#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../../_venv/bin/activate
python provisioner.py --action move_file\
  --src_file_path "./override.conf"\
  --dst_file_path "/etc/systemd/system/STRING_REPLACEMENT_SERVICE_NAME.service.d/override.conf"
