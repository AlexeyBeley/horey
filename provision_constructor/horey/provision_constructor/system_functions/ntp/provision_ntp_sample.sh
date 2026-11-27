#!/bin/bash
set -xe
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


#ntp
sudo apt purge ntp* -y
sudo apt purge sntp* -y
sudo apt purge chrony* -y

sudo timedatectl set-ntp false
source ../../_venv/bin/activate
python provisioner.py --action move_file\
  --src_file_path "./timesyncd.conf"\
  --dst_file_path "/etc/systemd/timesyncd.conf"

sudo timedatectl set-ntp true
sudo systemctl restart systemd-timedated
