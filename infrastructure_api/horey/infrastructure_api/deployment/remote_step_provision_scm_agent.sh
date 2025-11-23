#!/bin/bash

set -ex
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source "/opt/git/horey/build/_build/_venv/bin/activate"
python ./remote_step_provision_scm_agent.py
