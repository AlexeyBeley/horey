#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

source ../_venv/bin/activate
python system_function_common.py --action check_files_exist --files_paths "/usr/share/logstash/bin/logstash,/etc/systemd/system/logstash.service"
