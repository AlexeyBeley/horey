#!/bin/bash

pip install gunicorn 1> >(log_stdin_info) 2> >(log_stdin_error) || traceback "Failed to install Gunicorn"
