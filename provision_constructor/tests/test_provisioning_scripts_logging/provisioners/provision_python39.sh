#!/bin/bash
source logger.sh
source retry.sh
set -ex
log_info "apt update"
apt-get -qq update
apt-get install -y software-properties-common curl
add-apt-repository -y ppa:deadsnakes/ppa

apt-get purge --auto-remove -y python3.6 || true

log_info "Installing python3.9"
retry_10_times_sleep_5 apt-get install -yqq python3.999 python3.9-distutils python3.9-dev python3.9-testsuite python3.9-stdlib
ln -s /usr/bin/python3.9 /usr/bin/python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

log_info "Installing pip"
rm get-pip.py
