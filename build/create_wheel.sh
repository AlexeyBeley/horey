#!/bin/bash
set +xe

PACKAGE_NAME=$1
CURRENT_SCRIPT_FULL_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BUILD_TMP_DIR="${CURRENT_SCRIPT_FULL_PATH}/_build"
PACKAGE_TMP_DIR_FULL_PATH=${BUILD_TMP_DIR}/${PACKAGE_NAME}
ROOT_DIR="$(dirname "${CURRENT_SCRIPT_FULL_PATH}")"

echo "Copying cp -r ${ROOT_DIR}/${PACKAGE_NAME} ${BUILD_TMP_DIR}"
cp -r "${ROOT_DIR}/${PACKAGE_NAME}" "${BUILD_TMP_DIR}/"

echo "PACKAGE_TMP_DIR_FULL_PATH: ${PACKAGE_TMP_DIR_FULL_PATH}"
cd "${PACKAGE_TMP_DIR_FULL_PATH}"

if [ -d ${PACKAGE_TMP_DIR_FULL_PATH}/dist ]
then
 echo "Removing old package before creating new wheel: ${PACKAGE_TMP_DIR_FULL_PATH}"
 rm -rf ${PACKAGE_TMP_DIR_FULL_PATH}/dist/*
fi

python3 setup.py sdist bdist_wheel;