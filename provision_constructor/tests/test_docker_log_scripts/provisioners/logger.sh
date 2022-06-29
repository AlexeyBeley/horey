#!/bin/bash
#http://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

function log() {
  args="$*"
  echo "[$(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}]: ${args}"
}

function log_info() {
  args="$*"
  echo "[$(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}] [INFO]: ${args}"
}

function log_error() {
  args="$*"
  >&2 echo "[$(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}] [ERROR]: ${args}"
}

function traceback() {
  for (( idx=${#BASH_LINENO[@]}-1 ; idx>=0 ; idx-- )) ; do
    bash_line_number="${BASH_LINENO[idx]}"
    echo "$(get_abs_filename ${BASH_SOURCE[$((idx + 1))]}):${bash_line_number}"
  done
}
