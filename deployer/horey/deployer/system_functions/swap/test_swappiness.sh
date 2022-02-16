#!/bin/bash
set -xe

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

#1.  cat /proc/sys/vm/swappiness >> proc_swappiness.output
#2. cat /etc/sysctl.conf | grep vm.swappiness=1

python check_swap.py --action check_swappiness


