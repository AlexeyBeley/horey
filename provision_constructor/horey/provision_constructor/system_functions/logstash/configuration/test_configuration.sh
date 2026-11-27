#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../../_venv/bin/activate
python provisioner.py --action check_configuration_files
