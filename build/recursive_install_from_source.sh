#!/bin/bash
set -ex

CURRENT_SCRIPT_FULL_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pip3 install wheel

echo "Generating composed requirements.txt file"

ret=0
which python || export ret=1
if [[ $ret == '0' ]]; then
  python "${CURRENT_SCRIPT_FULL_PATH}/recursive_compose_requirements.py" "$@" --output_horey_file "${CURRENT_SCRIPT_FULL_PATH}/_build/required_horey_packages.txt" --output_requirements_file "${CURRENT_SCRIPT_FULL_PATH}/_build/requirements.txt"
 else
  python3 "${CURRENT_SCRIPT_FULL_PATH}/recursive_compose_requirements.py" "$@" --output_horey_file "${CURRENT_SCRIPT_FULL_PATH}/_build/required_horey_packages.txt" --output_requirements_file "${CURRENT_SCRIPT_FULL_PATH}/_build/requirements.txt"
fi


echo "Created recursive_compose_requirements"

pip3_path=$(which pip3)

ret=0
which python || export ret=1
if [[ $ret == '0' ]]; then
  python_subver=$(python -V |awk '{print $2}' | awk -F. '{print $2}')
 else
  python_subver=$(python3 -V |awk '{print $2}' | awk -F. '{print $2}')
fi

while read LINE; do
   set +ex
   pip3 uninstall -y "horey.${LINE}"
   set -ex

   rm -rf "${pip3_path%/*}/../lib/python3.${python_subver}/site-packages/horey/${LINE}"

   "${CURRENT_SCRIPT_FULL_PATH}/create_wheel.sh" "${LINE}"
   echo "After create_wheel.sh ${LINE}"

   pip3 install --force-reinstall --ignore-installed $(find "${CURRENT_SCRIPT_FULL_PATH}/_build/${LINE}/dist" -name "*.whl")
   echo "After pip3 install ${LINE}"

done <"${CURRENT_SCRIPT_FULL_PATH}/_build/required_horey_packages.txt"

pip3 install -r "${CURRENT_SCRIPT_FULL_PATH}/_build/requirements.txt"
