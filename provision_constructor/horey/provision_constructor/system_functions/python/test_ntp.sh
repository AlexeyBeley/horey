#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


ret=$(apt list --installed | grep ntp | wc -l)
if (( "$ret" > 0 )); then exit 1; fi

ret=$(apt list --installed | grep chrony | wc -l)
if (( "$ret" > 0 )); then exit 1; fi

systemctl status systemd-timesyncd


source ../../_venv/bin/activate

python provisioner.py --action compare_files\
  --src_file_path "./timesyncd.conf"\
  --dst_file_path "/etc/systemd/timesyncd.conf"

python provisioner.py --action check_systemd_service_status\
  --service_name "systemd-timesyncd"\
  --min_uptime "20"