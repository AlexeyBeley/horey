SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../_venv/bin/activate
python logstash_remote_provisioner.py --action add_logstash_configuration_files

