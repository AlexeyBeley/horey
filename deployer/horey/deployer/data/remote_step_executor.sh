#!/bin/bash
set +xe

STEP_SCRIPT_PATH=$1
STEP_SCRIPT_CONFIGURATION_FILE_PATH=$2
STEP_SCRIPT_FINISH_STATUS_FILE=$3
STEP_SCRIPT_OUTPUT_FILE_PATH=$4

DIR_PATH=$(dirname "$STEP_SCRIPT_OUTPUT_FILE_PATH")
if [ ! -d "${DIR_PATH}" ]
then
  mkdir -p "${DIR_PATH}"
fi

DIR_PATH=$(dirname "$STEP_SCRIPT_FINISH_STATUS_FILE")
if [ ! -d "${DIR_PATH}" ]
then
  mkdir -p "${DIR_PATH}"
fi

DIR_PATH=$(dirname "$STEP_SCRIPT_CONFIGURATION_FILE_PATH")
if [ ! -d "${DIR_PATH}" ]
then
  mkdir -p "${DIR_PATH}"
fi


if [ ! -f "${STEP_SCRIPT_CONFIGURATION_FILE_PATH}" ]
then
  touch "${STEP_SCRIPT_CONFIGURATION_FILE_PATH}"
fi

if [ ! -f "${STEP_SCRIPT_PATH}" ]
then
  echo "STEP ERROR: FILE '${STEP_SCRIPT_PATH}' DOES NOT EXIST" >> "${STEP_SCRIPT_OUTPUT_FILE_PATH}"
  echo -n "FAILURE" > "${STEP_SCRIPT_FINISH_STATUS_FILE}"
  exit 0;
fi

sudo chmod +x "${STEP_SCRIPT_PATH}"

echo "Executing: ${STEP_SCRIPT_PATH}" >> "${STEP_SCRIPT_OUTPUT_FILE_PATH}"
${STEP_SCRIPT_PATH} --configuration-file-path "${STEP_SCRIPT_CONFIGURATION_FILE_PATH}" >> "${STEP_SCRIPT_OUTPUT_FILE_PATH}" 2>&1

ret=$?

if [ ${ret} != 0 ]
then
  echo "STEP ERROR: ${STEP_SCRIPT_PATH} --configuration-file-path ${STEP_SCRIPT_CONFIGURATION_FILE_PATH} finished with ${ret}" >> "${STEP_SCRIPT_OUTPUT_FILE_PATH}"
  echo -n "FAILURE" > "${STEP_SCRIPT_FINISH_STATUS_FILE}"
  exit 0;
else
  echo "FINISHED: ${STEP_SCRIPT_PATH} --configuration-file-path ${STEP_SCRIPT_CONFIGURATION_FILE_PATH}" >> "${STEP_SCRIPT_OUTPUT_FILE_PATH}"
  echo -n "SUCCESS" > "${STEP_SCRIPT_FINISH_STATUS_FILE}"
  exit 0;
fi

exit 1;