set -xe
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https -y

source ../_venv/bin/activate
python system_function_common.py --action add_line_to_file --line 'deb https://artifacts.elastic.co/packages/7.x/apt stable main' --file_path "/etc/apt/sources.list.d/elastic-7.x.list"

sudo apt-get update
sudo apt-get install logstash -y
