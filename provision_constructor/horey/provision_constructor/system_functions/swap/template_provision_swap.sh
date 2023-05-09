
sudo swapoff -a
sudo fallocate -l STRING_REPLACEMENT_SWAP_SIZE_IN_GBG /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

