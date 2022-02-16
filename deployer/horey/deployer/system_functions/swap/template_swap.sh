sudo fallocate -l STRING_REPLACEMENT_SWAP_SIZE_IN_GBG /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

#permanent
#backup:
sudo cp /etc/fstab /etc/fstab.back

echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

#default swappiness is very bad 60- is for desktop
#ubuntu@ip-192-168-32-117:/var/log$ cat /proc/sys/vm/swappiness
#60

sudo sysctl vm.swappiness=1
#todo:
#This change it only temporary though. If you want to make it permanent, you can edit the
#/etc/sysctl.conf file and add the swappiness value in the end of the file:


echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf

#test
cat /proc/sys/vm/swappiness
