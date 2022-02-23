SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

sudo /usr/share/logstash/bin/logstash-plugin install logstash-output-opensearch
