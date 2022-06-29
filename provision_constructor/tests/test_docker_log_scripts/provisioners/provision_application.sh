#!/bin/bash

source logger.sh

log_info "Installing flask"
pip install flask==5.1.0 || traceback && exit 1