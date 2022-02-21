sudo sysctl vm.swappiness=1
#This change it only temporary though. If you want to make it permanent, you can edit the
echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf
