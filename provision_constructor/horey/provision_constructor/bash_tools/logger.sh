#!/bin/bash
#http://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

function log() {
  echo "${BASH_LINENO[@]}"
  echo "${BASH_SOURCE[@]}"
  #echo "${BASH_SOURCE[0]}:${BASH_LINENO[0]}"
}

function traceback() {
  counter=0
  for bash_line_number in "${BASH_LINENO[@]}"
  do
  echo "$(get_abs_filename ${BASH_SOURCE[counter]}):${bash_line_number}"
  counter=$((counter + 1))
  printf "\n"
done
}
