#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

set -e
set +x

./provision_python39.sh
./provision_gunicorn.sh
./provision_application.sh
