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
  args="$*"
  >&2 echo "($(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[0]}) [ERROR]: ${args}. Traceback:"

  for (( idx=${#BASH_LINENO[@]}-1 ; idx>=0 ; idx-- )) ; do
    bash_line_number="${BASH_LINENO[idx]}"
    >&2 echo "$(get_abs_filename ${BASH_SOURCE[$((idx + 1))]}):${bash_line_number}"
  done
  exit 1
}

function log_stdin_error() {
  while read line
   do
     if [ "${line}" != "" ]
      then
        echo "BASH_SOURCE:${BASH_SOURCE[*]}"
        echo "BASH_LINENO:${BASH_LINENO[*]}"

       >&2 log_formatted "($(basename "${BASH_SOURCE[2]}"):${BASH_LINENO[1]}) [ERROR]: ${line}"
     fi
   done
}

function log_stdin_info() {
  while read line
   do
     if [ "${line}" != "" ]
      then
       log_formatted "($(basename "${BASH_SOURCE[2]}"):${BASH_LINENO[1]}) [INFO]: ${line}"
     fi
   done
}

function logged(){
   "$@" 1> >(log_stdin_info) 2> >(log_stdin_error) || traceback "Failed to install Flask"

}