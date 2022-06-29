#!/bin/bash

source ../horey/provision_constructor/bash_tools/logger.sh


function test_log_info() {
    echo "#############"
    echo "before log info"
    log_info "Informative log string"
}

function test_log_error() {
    echo "#############"
    echo "before log error"
    log_error "Error log string"
}

function test_log_traceback() {
    echo "#############"
    echo "before traceback"
    traceback
}

function test_logs() {
    echo "########START###########"
    test_log_info
    test_log_error
    test_log_traceback
    echo "########END###########"
}

test_logs

# testing:
# echo ./bash_test_log.sh
# echo "$(./bash_test_log.sh)"
#./bash_test_log.sh 1>stdout.txt 2>stderr.txt

