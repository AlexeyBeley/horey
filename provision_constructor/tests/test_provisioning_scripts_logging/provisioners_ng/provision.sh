#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

set -e
set +x

source logger.sh

./provision_python39.sh 2> >(log_stdin_error) || traceback "Failed to run provision_python39.sh" && exit 1
./provision_gunicorn.sh  2> >(log_stdin_error) || traceback "Failed to run provision_gunicorn.sh" && exit 1
./provision_application.sh  2> >(log_stdin_error) || traceback "Failed to run provision_application.sh" && exit 1
