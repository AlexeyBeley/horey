#!/bin/bash
set +xe

PACKAGE_NAME=$1
CURRENT_SCRIPT_FULL_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BUILD_TMP_DIR="${CURRENT_SCRIPT_FULL_PATH}/_build/_venv"
PACKAGE_TMP_DIR_FULL_PATH=${BUILD_TMP_DIR}/${PACKAGE_NAME}
ROOT_DIR="$(dirname "${CURRENT_SCRIPT_FULL_PATH}")"

cp -r "${ROOT_DIR}/${PACKAGE_NAME}" "${BUILD_TMP_DIR}"

cd "${PACKAGE_TMP_DIR_FULL_PATH}"

if [ -d ${PACKAGE_TMP_DIR_FULL_PATH}/dist ]
then
 rm -rf ${PACKAGE_TMP_DIR_FULL_PATH}/dist/*
fi

python3 setup.py sdist bdist_wheel;