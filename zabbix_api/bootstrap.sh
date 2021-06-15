#mysql
wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.11-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.11-1_all.deb
sudo apt-get update
sudo apt-get install mysql-server -y




validate
sudo service mysql status
sudo mysql -u root -p

#zabbix
wget https://repo.zabbix.com/zabbix/5.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_5.4-1+ubuntu18.04_all.deb
sudo dpkg -i zabbix-release_5.4-1+ubuntu18.04_all.deb
sudo apt-get update
sudo apt-get install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent -y


sudo mysql -u root -p
create database zabbix character set utf8 collate utf8_bin;
create user zabbix@localhost identified by 'password';
grant all privileges on zabbix.* to zabbix@localhost;
quit;

zcat /usr/share/doc/zabbix-sql-scripts/mysql/create.sql.gz | mysql -uzabbix -p zabbix

sudo vi /etc/zabbix/zabbix_server.conf
DBPassword=password

sudo systemctl restart zabbix-server zabbix-agent apache2
sudo systemctl enable zabbix-server zabbix-agent apache2

