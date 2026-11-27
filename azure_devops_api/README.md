show databases
use {db_name}
        show databases        show database names
        show series           show series information
        show measurements     show measurement information
        show tag keys         show tag key information
        show field keys       show field key information

select * from {series}

API doc:
http://{url}:{port}/docs#tag/sources


backup
influxd backup

mv meta.00 /tmp/meta.00

restore
influxd restore -metadir /var/lib/influxdb/meta /tmp/


To restore data to a database that already exists:
1) influxd restore -portable -db telegraf -newdb telegraf_bak path-to-backup
> influxd restore -portable -db telegraf -newdb telegraf_bak path-to-backup
> influxd restore -online -db telegraf -newdb telegraf_bak path-to-backup
2) Sideload the data (using a SELECT ... INTO statement) into the existing target database and drop the temporary database.
> USE telegraf_bak
> SELECT * INTO telegraf..:MEASUREMENT FROM /.*/ GROUP BY *
> DROP DATABASE telegraf_bak

influx -execute 'SHOW DATABASES'