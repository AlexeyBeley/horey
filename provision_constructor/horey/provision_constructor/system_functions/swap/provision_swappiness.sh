
sudo sysctl vm.swappiness=1
#todo:
#This change it only temporary though. If you want to make it permanent, you can edit the
#/etc/sysctl.conf file and add the swappiness value in the end of the file:


echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf

