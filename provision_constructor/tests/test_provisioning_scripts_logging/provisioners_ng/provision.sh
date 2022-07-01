#!/bin/bash

set -e
set +x

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

./provision_python39.sh
./provision_gunicorn.sh
./provision_application.sh
