#!/bin/bash
set -ex
sudo DEBIAN_FRONTEND=noninteractive apt update
export PYTHON=$(which python >> /dev/null && echo "python" || echo "python3")

export VERSION_STRING=$(${PYTHON} -V)
export VERSION_NUMBER=${VERSION_STRING#Python }
export MAJOR_MINOR_VERSION=${VERSION_NUMBER%.*}

sudo NEEDRESTART_MODE=a apt install "python${MAJOR_MINOR_VERSION}-venv" -yqq
#wget https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/pip_api_make.py

git clone --branch "cicd_api" https://github.com/AlexeyBeley/horey.git
cd horey
${PYTHON} pip_api/horey/pip_api/pip_api_make.py --install horey.provision_constructor --pip_api_configuration pip_api_configuration.py
