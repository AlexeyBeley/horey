#!/bin/bash
#http://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

function log_formatted() {
  args="$*"
  echo "[$(date +"%Y/%m/%d %H:%M:%S")] $args"
}

function log_info() {
  args="$*"
  log_formatted "($(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}) [INFO]: ${args}"
}

function log_error() {
  >&2 log_formatted "($(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}) [ERROR]: ${args}"
}

function traceback() {
  #args="$*"
  #echo "($(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}) [ERROR]: ${args}. Traceback:"

  for (( idx=${#BASH_LINENO[@]}-1 ; idx>=0 ; idx-- )) ; do
    echo "idx: ${idx}"
    bash_line_number="${BASH_LINENO[idx]}"
    echo "$(get_abs_filename ${BASH_SOURCE[$((idx + 1))]}):${bash_line_number}"
  done
  exit 1
}

function log_stdin_error() {
  while read line
   do
     if [ "${line}" != "" ]
      then
       >&2 log_formatted "($(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}) [ERROR]: ${line}"
     fi
   done
}

function log_stdin_info() {
  while read line
   do
     if [ "${line}" != "" ]
      then
       log_formatted "($(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}) [INFO]: ${line}"
     fi
   done
}
