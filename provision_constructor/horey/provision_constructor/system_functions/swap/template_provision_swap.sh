sudo fallocate -l STRING_REPLACEMENT_SWAP_SIZE_IN_GBG /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

#backup:
sudo cp /etc/fstab /etc/fstab.back

#permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab