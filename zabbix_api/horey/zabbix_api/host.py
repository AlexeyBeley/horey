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

        super().__init__(dict_src, from_cache=from_cache)

        init_options = {
            "hostid": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "proxy_hostid": self.init_default_attr,
            "host": self.init_default_attr,
            "status": self.init_default_attr,
            "lastaccess": self.init_default_attr,
            "ipmi_authtype": self.init_default_attr,
            "ipmi_privilege": self.init_default_attr,
            "ipmi_username": self.init_default_attr,
            "ipmi_password": self.init_default_attr,
            "maintenanceid": self.init_default_attr,
            "maintenance_status": self.init_default_attr,
            "maintenance_type": self.init_default_attr,
            "maintenance_from": self.init_default_attr,
            "name": self.init_default_attr,
            "flags": self.init_default_attr,
            "templateid": self.init_default_attr,
            "description": self.init_default_attr,
            "tls_connect": self.init_default_attr,
            "tls_accept": self.init_default_attr,
            "tls_issuer": self.init_default_attr,
            "tls_subject": self.init_default_attr,
            "proxy_address": self.init_default_attr,
            "auto_compress": self.init_default_attr,
            "discover": self.init_default_attr,
            "custom_interfaces": self.init_default_attr,
            "uuid": self.init_default_attr,
            "groups": self.init_default_attr,
            "interfaces": self.init_default_attr,
            "parentTemplates": self.init_default_attr,
            "vendor_name": self.init_default_attr,
            "vendor_version": self.init_default_attr,
            "inventory_mode": self.init_default_attr,
            "active_available": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self, validate=True):
        """
        {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": "Example host",
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": "192.168.3.1",
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": "50"
                    }
                ],
                "templates": [
                    {
                        "templateid": "10338"
                    }
                ],
                "inventory_mode": 0,
                "inventory": {
                    "macaddress_a": "01234",
                    "macaddress_b": "56768"
                }
            },
            "auth": "038e1d7b1735c6a5436ee9eae095879e",
            "id": 1
        }
        """
        if validate:
            if self.host != self.name:
                raise ValueError(f"self.host= {self.host} != self.name = {self.name}")

        request = {"host": self.host, "status": self.status,
                   "groups": [{"groupid": group["groupid"]} for group in self.groups], "interfaces": [
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
        request["hostid"] = self.id
        del request["interfaces"]
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
        request = [self.id]
        return request
