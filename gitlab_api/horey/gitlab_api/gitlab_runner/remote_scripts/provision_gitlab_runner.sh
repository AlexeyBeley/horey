#!/bin/bash

set -ex
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

python3.8 ./provision_gitlab_runner.py
