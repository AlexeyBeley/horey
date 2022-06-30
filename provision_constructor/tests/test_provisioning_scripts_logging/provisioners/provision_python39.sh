#!/bin/bash
source logger.sh
source retry.sh
apt-get -qq update
apt-get install -y software-properties-common curl
add-apt-repository -y ppa:deadsnakes/ppa

apt-get purge --auto-remove -y python3.6 || true

retry_10_times_sleep_5 apt-get install -yqq python3.9 python3.9-distutils python3.9-dev python3.9-testsuite python3.9-stdlib
ln -s /usr/bin/python3.9 /usr/bin/python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

rm get-pip.py
