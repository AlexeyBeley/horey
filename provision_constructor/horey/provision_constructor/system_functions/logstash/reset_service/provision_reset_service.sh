SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"


#source ../_venv/bin/activate
#python provisioner.py --action perform_comment_line_replacement\
#  src_file STRING_REPLACEMENT_FILTER_FILE_NAME\
#  dst_file "/etc/logstash/conf.d/STRING_REPLACEMENT_PIPELINE_NAME.conf"\
#  comment_line "#OUTPUT_BOTOM"

set -xe

logstash_pid=$(ps aux | grep 'logstash' | grep 'java' | awk '{print $2}')
if [ -n "${logstash_pid}" ]
then
      sudo kill -s 9 "${logstash_pid}"
else
      sudo systemctl restart logstash
fi
