#!/bin/bash
set -xe
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


sudo apt-get install -yqq python3.8 python3.8-distutils python3.8-dev python3.8-testsuite python3.8-stdlib
sudo ln -s /usr/bin/python3.8 /usr/bin/python3