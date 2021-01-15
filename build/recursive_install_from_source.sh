#!/bin/bash
set +ex

CURRENT_SCRIPT_FULL_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
python3 "${CURRENT_SCRIPT_FULL_PATH}/recursive_compose_requirements.py" "$@" --output_file "${CURRENT_SCRIPT_FULL_PATH}/required_horey_packages.txt"

#echo $PWD
#make install_from_source-h_logger
#cat ./required_horey_packages.txt