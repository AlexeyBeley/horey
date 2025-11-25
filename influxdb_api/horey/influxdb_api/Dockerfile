# Use the official InfluxDB 1.8 image as the base
FROM influxdb:1.8

# Optionally, copy a custom configuration file
# This assumes you have a file named 'influxdb.conf' in the same directory as your Dockerfile
# COPY influxdb.conf /etc/influxdb/influxdb.conf

# Optionally, add an entrypoint script for initialization tasks
# For example, to create a database on startup
# COPY init-influxdb.sh /docker-entrypoint-initdb.d/
# RUN chmod +x /docker-entrypoint-initdb.d/init-influxdb.sh

# Expose the default InfluxDB port
EXPOSE 8086

# The default command for the InfluxDB image will start the server
# CMD ["influxd"]