SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


source ../_venv/bin/activate
python provisioner.py --action perform_comment_line_replacement\
  src_file STRING_REPLACEMENT_OUTPUT_OPENSEARCH_FILE_NAME\
  dst_file "/etc/logstash/conf.d/STRING_REPLACEMENT_PIPELINE_NAME.conf"\
  comment_line "#OUTPUT_BOTOM"

