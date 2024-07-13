#!/bin/bash
set -ex
sudo DEBIAN_FRONTEND=noninteractive apt update
#wget https://raw.githubusercontent.com/AlexeyBeley/horey/main/pip_api/horey/pip_api/pip_api_make.py
git clone https://github.com/AlexeyBeley/horey.git
#sudo chmod 777 horey
cd horey

python3 pip_api/horey/pip_api/pip_api_make.py --install horey.provision_constructor --pip_api_configuration pip_api_configuration.py
