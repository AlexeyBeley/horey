#!/bin/bash

set -ex
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source "/opt/git/horey/build/_build/_venv/activate"
