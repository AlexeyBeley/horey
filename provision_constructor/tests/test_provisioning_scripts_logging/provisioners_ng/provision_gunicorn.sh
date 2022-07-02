#!/bin/bash

source logger.sh

logged pip install gunicorn

#pip install gunicorn 1> >(log_stdin_info) 2> >(log_stdin_error) || traceback "Failed to install Gunicorn"
