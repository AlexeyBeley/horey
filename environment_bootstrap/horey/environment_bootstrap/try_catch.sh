#!/bin/bash
set -e

try () {
  if [[ $- == *e* ]]
  then
     E_OPTION="-e"
  else
     E_OPTION="+e"
  fi

  set +e

  echo $1

  function_ret=$?

  echo "${function_ret}"

  set "${E_OPTION}"
}

protected () {
  #cat /etc/sudoers
  ls /tmp
}

try protected
#cat /etc/sudoers