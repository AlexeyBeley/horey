"""
Zabbix host.

"""
from horey.zabbix_api.zabbix_object import ZabbixObject


class Host(ZabbixObject):
    """
    Main class.
    """
    def __init__(self, dict_src, from_cache=False):
        self.groups = []
        self.name = None
        self.host = None
        self.interfaces = []
        self.parent_templates = []
        self.status = None
        self.hostid = None
        self.proxyid = None
        self.ipmi_authtype = None
        self.ipmi_privilege = None
        self.ipmi_username = None
        self.ipmi_password = None
        self.maintenanceid = None
        self.maintenance_status = None
        self.maintenance_type = None
        self.maintenance_from = None
        self.flags = None
        self.templateid = None
        self.description = None
        self.tls_connect = None
        self.tls_accept = None
        self.tls_issuer = None
        self.tls_subject = None
        self.custom_interfaces = None
        self.uuid = None
        self.vendor_name = None
        self.vendor_version = None
        self.proxy_groupid = None
        self.monitored_by = None
        self.wizard_ready = None
        self.readme = None
        self.inventory_mode = None
        self.active_available = None
        self.assigned_proxyid = None
        self.hostgroups = None
        self.proxy_hostid = None
        self.proxy_address = None
        self.auto_compress = None

        super().__init__(dict_src, from_cache=from_cache)

        self.init_attrs(dict_src)

    def generate_create_request(self, validate=True):
        """
        Host request

        :param validate:
        :return:
        """

        if validate:
            if self.host != self.name:
                raise ValueError(f"self.host= {self.host} != self.name = {self.name}")

        request = {"host": self.host, "status": self.status,
                   "groups": [{"groupid": group["groupid"]} for group in self.hostgroups], "interfaces": [
                {
                    "ip": interface["ip"],
                    "type": interface["type"],
                    "main": interface["main"],
                    "useip": interface["useip"],
                    "dns": interface["dns"],
                    "port": interface["port"],
                }
                for interface in self.interfaces
            ], "templates": [
                {"templateid": template["templateid"]} for template in self.parent_templates
            ]}

        return request

    def generate_update_request(self):
        """
        Standard.

        :return:
        """

        request = self.generate_create_request()
        request["hostid"] = self.hostid
        del request["interfaces"]
        del request["host"] # is not working in new API
        return request

    def generate_delete_request(self):
        """
        {
        "jsonrpc": "2.0",
        "method": "host.delete",
        "params": [
            "13",
            "32"
        ],
        "auth": "038e1d7b1735c6a5436ee9eae095879e",
        "id": 1
        }"""
        request = [self.hostid]
        return request
