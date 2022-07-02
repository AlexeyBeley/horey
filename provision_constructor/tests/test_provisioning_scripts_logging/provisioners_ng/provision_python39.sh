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
ln -s /usr/bin/python3.9 /usr/bin/python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py 1> >(log_stdin_info) 2> >(log_stdin_error) || traceback "Failed to install Gunicorn"

rm get-pip.py
