#!/bin/bash

set -ex
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

source horey/build/_build/_venv/bin/activate
python3 step_provision_constructor_apply.py
