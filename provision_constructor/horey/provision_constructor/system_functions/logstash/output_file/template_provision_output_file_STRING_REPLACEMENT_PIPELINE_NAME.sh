#!/bin/bash
set -ex

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../../_venv/bin/activate
python provisioner.py --action perform_comment_line_replacement\
  --src_file_path STRING_REPLACEMENT_OUTPUT_FILE_PATH\
  --dst_file_path "/etc/logstash/conf.d/STRING_REPLACEMENT_PIPELINE_NAME.conf"\
  --comment_line "#OUTPUT_BOTOM"

