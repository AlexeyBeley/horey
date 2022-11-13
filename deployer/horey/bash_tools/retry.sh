#!/bin/bash

function preserve_e_option ()  {
  if [[ $- == *e* ]]
  then
     E_OPTION="-e"
  else
     E_OPTION="+e"
  fi
}

restore_e_option () {
    set "${E_OPTION}"
}

function unlock_frontend_file () {
  PID=$(sudo lsof /var/lib/dpkg/lock-frontend | awk '/[0-9]+/{print $2}')
  if [ -n "${PID}" ]
  then
      sudo kill -s 9 "${PID}" || true
  fi
}

function retry_10_times_sleep_5 () {
preserve_e_option
set +e
for VARIABLE in {1..10}
do
  unlock_frontend_file
	echo "$@"
  "$@"
  return_code=$?
  if [ "$return_code" == 0 ]
  then
      restore_e_option
      return 0
  fi
  echo "Retry ${VARIABLE}/10 going to sleep for 5 seconds"
  sleep 5s
done

restore_e_option
return "${return_code}"
}

function retry_3_times_sleep_5_with_timeout_30 () {
set +e
for VARIABLE in {1..3}
do
  output=$(timeout --kill-after=30 30 "$@" 2>&1)
  return_code=$?
  if [ "$return_code" == 0 ]
  then
      return 0
  fi
  sleep 5s
  echo "Retry ${VARIABLE}/3"
done

set -e
return "${return_code}"
}
