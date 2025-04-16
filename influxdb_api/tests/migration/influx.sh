
# Deploy influx
# Deploy kapacitor in silent mode - do not send alerts

# Configure old influx -> replicate new influx
# Configure New influx -> replicate new kapacitor

# dump old data for 1 year
# restore into new influx new_table
# insert into old_table from new_table




# perform the backup
export NEW_SERVER_ADDRESS=""
export BACKUP_DB_NAME=""
mkdir ~/influx_backup && cd $_
# remote:
influxd backup -host "${NEW_SERVER_ADDRESS}":8088 -since 2024-03-03T00:00:00Z -portable -db "${BACKUP_DB_NAME}" ./
# local:
influxd backup -since 2024-03-03T00:00:00Z -portable -db "${BACKUP_DB_NAME}" ./


scp -r ~/influx_backup "${NEW_SERVER_ADDRESS}":/home/ubuntu/influx_backup

# install influxdb with horey/provision_constructor/system_functions/influxdb/provision_influx.sh

# restore the backup
influxd restore -portable -db "${BACKUP_DB_NAME}" /home/ubuntu/influx_backup


# create subsription
influx -execute "CREATE SUBSCRIPTION \"new_influx\" ON \"${BACKUP_DB_NAME}\".\"autogen\" DESTINATIONS ALL 'http://${NEW_SERVER_ADDRESS}:8086'"

#swap on the destination
sudo swapoff -a
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab


# Restore the rest of the data
To restore data to a database that already exists:
1) influxd restore -portable -db telegraf -newdb telegraf_bak path-to-backup
> influxd restore -portable -db telegraf -newdb telegraf_bak path-to-backup
> influxd restore -online -db telegraf -newdb telegraf_bak path-to-backup
2) Sideload the data (using a SELECT ... INTO statement) into the existing target database and drop the temporary database.
> USE telegraf_bak
> SELECT * INTO telegraf..:MEASUREMENT FROM /.*/ GROUP BY *
> DROP DATABASE telegraf_bak

influx -execute 'SHOW DATABASES'

export BACKUP_DB_NAME="db_name"
influxd restore -portable -db "${BACKUP_DB_NAME}" -newdb "${BACKUP_DB_NAME}_backup" /home/ubuntu/influx_backup
SELECT * INTO "${BACKUP_DB_NAME}".autogen.:MEASUREMENT FROM "${BACKUP_DB_NAME}_backup".autogen./.*/ GROUP BY *


# backup missing data
influxd backup -since 2025-03-20T00:00:00Z -portable -db "${BACKUP_DB_NAME}" ./
