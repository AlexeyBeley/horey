#!/bin/bash

set -ex
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

sudo mkdir -p /opt/jenkins_jobs_starter

python3.8 ./provision_gitlab_runner.py

sudo chmod +x ./register_gitlab_runner.sh
./register_gitlab_runner.sh

sudo cp ./jenkins_job_starter.py /opt/jenkins_jobs_starter/
