#!/bin/bash

source ../horey/provision_constructor/bash_tools/logger.sh


function koo() {
    log "$@"
}

function foo() {
    koo "$@"
}

foo "$@"