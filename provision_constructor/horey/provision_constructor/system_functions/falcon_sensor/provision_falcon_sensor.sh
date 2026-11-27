#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


export CROWDSTRIKE_FALCON_SENSOR_CID=""
export DOWNLOAD_LINK=""

set +xe
sudo apt-get install libnl-3-200 -y
sudo apt-get install libnl-genl-3-200 -y
wget "${DOWNLOAD_LINK}"

mv falcon-senso* falcon-sensor.deb
sudo dpkg -i ./falcon-sensor.deb
sudo /opt/CrowdStrike/falconctl -sf --cid="${CROWDSTRIKE_FALCON_SENSOR_CID}"
sudo systemctl start falcon-sensor
