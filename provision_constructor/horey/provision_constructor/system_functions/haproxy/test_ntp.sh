#influxdb
export KEY_FILE_PATH="/etc/apt/trusted.gpg.d/influxdb.gpg"
if [ ! -f "${KEY_FILE_PATH}" ]
then
curl -s https://repos.influxdata.com/influxdb.key | sudo  gpg --dearmor -o "${KEY_FILE_PATH}"
fi

export DISTRIB_ID=$(lsb_release -si)
export DISTRIB_CODENAME=$(lsb_release -sc)

echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" > influxdb.list
sudo mv influxdb.list /etc/apt/sources.list.d/

sudo apt-get update
sudo apt-get install -y influxdb
sudo systemctl unmask influxdb.service
sudo systemctl start influxdb
sudo apt install influxdb-client -y