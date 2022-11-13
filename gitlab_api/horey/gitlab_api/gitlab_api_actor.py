from zabbix_api import ZabbixAPI, ZabbixAPIException

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = "http://"

zapi = ZabbixAPI(ZABBIX_SERVER)

# Login to the Zabbix API


def main():
    api = ZabbixAPI()
    zapi.login("Admin", "zabbix")

    host_name = "example.com"

    hosts = zapi.host.get(filter={"host": host_name}, selectInterfaces=["interfaceid"])
    if hosts:
        host_id = hosts[0]["hostid"]
        print("Found host id {0}".format(host_id))

        try:
            item = zapi.item.create(
                hostid=host_id,
                name="Used disk space on $1 in %",
                key_="vfs.fs.size[/,pused]",
                type=0,
                value_type=3,
                interfaceid=hosts[0]["interfaces"][0]["interfaceid"],
                delay=30,
            )
        except ZabbixAPIException as e:
            print(e)
            raise

        print(
            "Added item with itemid {0} to host: {1}".format(
                item["itemids"][0], host_name
            )
        )
    else:
        print("No hosts found")


if __name__ == "__main__":
    main()
