#!/bin/bash

set -xe
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../_venv/bin/activate
python check_swap.py --action check_swap_size --swap_size STRING_REPLACEMENT_SWAP_SIZE_IN_GB
