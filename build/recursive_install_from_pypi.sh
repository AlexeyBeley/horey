#!/bin/bash
set -ex

CURRENT_SCRIPT_FULL_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pip3 install wheel

echo "Generating composed requirements.txt file"

python3 "${CURRENT_SCRIPT_FULL_PATH}/recursive_compose_requirements.py" "$@" --output_horey_file "${CURRENT_SCRIPT_FULL_PATH}/_build/required_horey_packages.txt" --output_requirements_file "${CURRENT_SCRIPT_FULL_PATH}/_build/requirements.txt"

echo "Created recursive_compose_requirements"

while read LINE; do
   pip3 install "horey.${LINE}"
   echo "After pip3 install ${LINE}"

done <"${CURRENT_SCRIPT_FULL_PATH}/_build/required_horey_packages.txt"

pip3 install -r "${CURRENT_SCRIPT_FULL_PATH}/_build/requirements.txt"
