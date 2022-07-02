#!/bin/bash
source logger.sh
source retry.sh

log_info "Updating apt packages list"
logged retry_10_times_sleep_5 apt-get -qq update
log_info "Updated apt packages list"
logged retry_10_times_sleep_5 apt-get install -y software-properties-common curl
logged retry_10_times_sleep_5 add-apt-repository -y ppa:deadsnakes/ppa

logged retry_10_times_sleep_5 apt-get purge --auto-remove -y python3.6

logged retry_10_times_sleep_5 apt-get install -yqq python3.9 python3.9-distutils python3.9-dev python3.9-testsuite python3.9-stdlib
logged_ignore_exception ln -s /usr/bin/python3.9 /usr/bin/python
logged curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
logged python get-pip.py

logged rm get-pip.py
