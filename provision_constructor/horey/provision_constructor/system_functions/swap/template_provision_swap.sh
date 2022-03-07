set +e
sudo fallocate -l STRING_REPLACEMENT_SWAP_SIZE_IN_GBG /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
set -e
#backup:
sudo cp /etc/fstab /etc/fstab.back


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

#permanent
source ../_venv/bin/activate
python system_function_common.py --action add_line_to_file --line '/swapfile none swap sw 0 0' --file_path "/etc/fstab"
