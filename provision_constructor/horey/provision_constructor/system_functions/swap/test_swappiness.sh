#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


#cat /proc/sys/vm/swappiness >> proc_swappiness.output
source ../_venv/bin/activate
python check_swap.py --action check_swappiness


