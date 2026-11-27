sudo apt update && sudo apt-get upgrade
sudo apt install git
sudo apt install build-essential cmake doxygen graphviz miniupnpc pkg-config libboost-all-dev libcurl4-openssl-dev libgtest-dev libminiupnpc-dev libreadline-dev libssl-dev libunbound-dev libunwind8-dev libzmq3-dev libzmq3-dev libpgm-dev libsodium-dev


cd /usr/src/gtest
sudo cmake .
sudo make -j2
sudo mv libg* /usr/lib/

mkdir /opt/source
cd /opt/source

git clone --recursive https://github.com/monero-project/monero
cd monero
make -j2 release # -j4 for 4 threads etc

sudo cp ./build/release/bin/* /usr/local/bin/

mkdir ~/.bitmonero
cd ~/.bitmonero
touch monerod.conf