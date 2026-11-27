sudo sysctl vm.swappiness=1
#This change it only temporary though. If you want to make it permanent, you can edit the

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

source ../_venv/bin/activate
python system_function_common.py --action add_line_to_file --line 'vm.swappiness=1' --file_path "/etc/sysctl.conf"
