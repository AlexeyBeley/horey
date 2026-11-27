#!/bin/bash
set -ex
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

sudo DEBIAN_FRONTEND=noninteractive apt update -yqq
sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt install "python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')-venv" -yqq
#wget https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/pip_api_make.py

if [ ! -d horey ]; then
    echo "Directory 'horey' does not exist. Creating it now."
    git clone https://github.com/AlexeyBeley/horey.git
fi

cd horey

python3 pip_api/horey/pip_api/pip_api_make.py --install horey.provision_constructor --pip_api_configuration pip_api_configuration.py
