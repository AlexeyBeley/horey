#!/bin/bash

source logger.sh

logged pip install flask==5.1.0

#pip install flask==5.1.0 1> >(log_stdin_info) 2> >(log_stdin_error) || traceback "Failed to install Flask"
