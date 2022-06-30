#!/bin/bash

source logger.sh

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
  PID=$(lsof /var/lib/dpkg/lock-frontend | awk '/[0-9]+/{print $2}')
  if [ -n "${PID}" ]
  then
      kill -s 9 "${PID}" || true
  fi
}

function retry_10_times_sleep_5 () {
export -f log_error
preserve_e_option
set +e
for VARIABLE in {1..2}
do
  unlock_frontend_file
	log_info "Running: '$*'"
  "$@"  2>  >(xargs -0 -n1 -I '{}' /bin/bash -c 'log_error "{}"')
  return_code=$?
  if [ "$return_code" == 0 ]
  then
      restore_e_option
      return 0
  fi
  echo "Retry ${VARIABLE}/10 going to sleep for 5 seconds"
  sleep 5
traceback
exit 1
done

restore_e_option
return "${return_code}"
}


