#!/bin/bash
set -ex
sudo DEBIAN_FRONTEND=noninteractive apt update
sudo NEEDRESTART_MODE=a apt install python3.10-venv -yqq
#wget https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/pip_api_make.py

#git clone https://github.com/AlexeyBeley/horey.git
git clone -b pip_api_fix_to_make https://github.com/AlexeyBeley/horey.git
cd horey
python3 pip_api/horey/pip_api/pip_api_make.py --install horey.provision_constructor --pip_api_configuration pip_api_configuration.py
