#!/bin/bash

source logger.sh

pip install flask==5.1.0 || traceback && exit 1