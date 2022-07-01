#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

set -e
set +x

source logger.sh

./provision_application.sh 1> >(log_stdin_info)
./provision_python39.sh 1> >(log_stdin_info)
./provision_gunicorn.sh 1> >(log_stdin_info)
