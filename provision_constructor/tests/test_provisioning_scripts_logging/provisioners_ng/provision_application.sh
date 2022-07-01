#!/bin/bash

source logger.sh

pip install flask==5.1.0 || traceback "Failed to install flask" && exit 1