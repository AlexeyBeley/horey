#influxdb
set -ex

export KEY_FILE_PATH="/etc/apt/trusted.gpg.d/influxdb.gpg"
if [ ! -f "${KEY_FILE_PATH}" ]
then
curl -s https://repos.influxdata.com/influxdb.key | sudo  gpg --dearmor -o "${KEY_FILE_PATH}"
fi




check_exists=$(influx -execute 'SHOW SUBSCRIPTIONS')
if [[ -z "${check_exists}" ]];then
influx -execute 'CREATE DATABASE one'
influx -execute 'CREATE DATABASE two'
influx -execute "CREATE SUBSCRIPTION \"kapacitor_new\" ON \"one\".\"autogen\" DESTINATIONS ALL 'http://addr:9092'"
fi


# from binaries:

#!/bin/bash
set -x
mkdir installer && cd $_
wget https://download.influxdata.com/influxdb/releases/influxdb-1.11.8-linux-arm64.tar.gz
tar xvf influxdb-1.11.8-linux-arm64.tar.gz
sudo chown root:root ./*
sudo mv /usr/bin/influx /usr/bin/influx_old
sudo mv /usr/bin/influxd /usr/bin/influxd_old
sudo mv influx /usr/bin/influx
sudo mv influxd /usr/bin/influxd
sudo systemctl restart influxdb