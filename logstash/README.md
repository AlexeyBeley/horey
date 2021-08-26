
#Debug
/usr/share/logstash/bin/logstash
output { stdout { codec => rubydebug } }

sudo /usr/share/logstash/bin/logstash --debug -f /etc/logstash/conf.d/debug.conf
