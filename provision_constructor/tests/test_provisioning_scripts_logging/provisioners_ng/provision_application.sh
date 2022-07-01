#!/bin/bash

source logger.sh

pip install flask==5.1.0 2> >(log_stdin_error) || traceback "Failed to install flask"
