#influxdb
set -ex

sudo apt-get install haproxy -y
sudo apt-get install socat -y
sudo systemctl enable haproxy.service