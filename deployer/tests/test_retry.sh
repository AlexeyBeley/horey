#!/bin/bash
set -e

source ../horey/bash_tools/retry.sh

function test_retry_10_times_sleep_5_valid () {

    retry_10_times_sleep_5 ls
    ret=$?
    echo "Test finished with status ${ret} expected 0"
}

function test_retry_10_times_sleep_5_invalid () {
    set -e
    set -x
    retry_10_times_sleep_5 unexisting_command
    ret=$?
    echo "Test finished with status ${ret} expected > 0"
}

function test_retry_10_times_sleep_5_valid_function () {
  function valid_function () {
    echo 1
    }
  retry_10_times_sleep_5 valid_function

}

function test_retry_10_times_sleep_5_valid_function_with_args () {
  function valid_function () {
    echo "$1";
    echo "$2"
    }
  retry_10_times_sleep_5 valid_function 1 2

}

#test_retry_10_times_sleep_5_valid
test_retry_10_times_sleep_5_invalid
#test_retry_10_times_sleep_5_valid_function
#test_retry_10_times_sleep_5_valid_function_with_args

