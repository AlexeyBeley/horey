"""
Shamelessly stolen from:
https://github.com/lukecyca/pyzabbix
"""
import pdb

import requests
import json
from horey.h_logger import get_logger
from horey.zabbix_api.zabbix_api_configuration_policy import (
    ZabbixAPIConfigurationPolicy,
)
from horey.zabbix_api.host import Host

logger = get_logger()


class ZabbixAPIException(Exception):
    """generic zabbix api exception
    code list:
         -32700 - invalid JSON. An error occurred on the server while parsing the JSON text (typo, wrong quotes, etc.)
         -32600 - received JSON is not a valid JSON-RPC Request
         -32601 - requested remote-procedure does not exist
         -32602 - invalid method parameters
         -32603 - Internal JSON-RPC error
         -32400 - System error
         -32300 - Transport error
         -32500 - Application error
    """

    def __init__(self, *args, **kwargs):
        super(ZabbixAPIException, self).__init__(*args)

        self.error = kwargs.get("error", None)


class ZabbixAPI(object):
    def __init__(self, configuration: ZabbixAPIConfigurationPolicy = None):
        if configuration.session is not None:
            self.session = configuration.session
        else:
            self.session = requests.Session()

        # Default headers for all requests
        self.session.headers.update(
            {
                "Content-Type": "application/json-rpc",
                "User-Agent": "python/pyzabbix",
                "Cache-Control": "no-cache",
            }
        )

        self.configuration = configuration
        self.auth = ""
        self.id = 0

        self.timeout = configuration.timeout

        self.url = configuration.url
        logger.info(f"JSON-RPC Server Endpoint: {self.url}")
        self.hosts = None

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if isinstance(exception_value, (ZabbixAPIException, type(None))):
            if self.is_authenticated:
                self.user.logout()
            return True

    def login(self):
        """Convenience method for calling user.authenticate and storing the resulting auth token
        for further commands.
        If use_authenticate is set, it uses the older (Zabbix 1.8) authentication command
        :param password: Password used to login into Zabbix
        :param user: Username used to login into Zabbix
        """

        # If we have an invalid auth token, we are not allowed to send a login
        # request. Clear it before trying.
        self.auth = ""
        if self.configuration.user_authenticate:
            raise NotImplementedError()
            # self.auth = self.user.authenticate(user=user, password=password)
            # self.auth = self.user.login(user=user, password=password)
        elif self.configuration.token_authenticate:
            self.auth = self.configuration.auth_token

    def check_authentication(self):
        """Convenience method for calling user.checkAuthentication of the current session"""
        return self.user.checkAuthentication(sessionid=self.auth)

    @property
    def is_authenticated(self):
        try:
            self.user.checkAuthentication(sessionid=self.auth)
        except ZabbixAPIException:
            return False
        return True

    def confimport(self, confformat="", source="", rules=""):
        """Alias for configuration.import because it clashes with
        Python's import reserved keyword
        :param rules:
        :param source:
        :param confformat:
        """

        return self.do_request(
            method="configuration.import",
            params={"format": confformat, "source": source, "rules": rules},
        )["result"]

    def api_version(self):
        return self.apiinfo.version()

    def do_request(self, method, params=None):
        request_json = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.id,
        }

        # We don't have to pass the auth token if asking for the apiinfo.version or user.checkAuthentication
        if (
            self.auth
            and method != "apiinfo.version"
            and method != "user.checkAuthentication"
        ):
            request_json["auth"] = self.auth

        logger.debug(
            "Sending: %s", json.dumps(request_json, indent=4, separators=(",", ": "))
        )
        response = self.session.post(
            self.url, data=json.dumps(request_json), timeout=self.timeout
        )
        logger.debug("Response Code: %s", str(response.status_code))

        # NOTE: Getting a 412 response code means the headers are not in the
        # list of allowed headers.
        response.raise_for_status()

        if not len(response.text):
            raise ZabbixAPIException("Received empty response")

        try:
            response_json = json.loads(response.text)
        except ValueError:
            raise ZabbixAPIException("Unable to parse json: %s" % response.text)
        logger.debug(
            "Response Body: %s",
            json.dumps(response_json, indent=4, separators=(",", ": ")),
        )

        self.id += 1

        if "error" in response_json:  # some exception
            if (
                "data" not in response_json["error"]
            ):  # some errors don't contain 'data': workaround for ZBX-9340
                response_json["error"]["data"] = "No data"
            msg = "Error {code}: {message}, {data}".format(
                code=response_json["error"]["code"],
                message=response_json["error"]["message"],
                data=response_json["error"]["data"],
            )
            raise ZabbixAPIException(
                msg, response_json["error"]["code"], error=response_json["error"]
            )

        return response_json

    def __getattr__(self, attr):
        """Dynamically create an object class (ie: host)"""
        return ZabbixAPIObjectClass(attr, self)

    def init_hosts(self):
        self.login()
        host_dicts = self.host.get(
            selectGroups="extend",
            selectInterfaces=[
                "interfaceid",
                "ip",
                "type",
                "main",
                "useip",
                "dns",
                "port",
            ],
            selectParentTemplates=["templateid", "name"],
        )

        self.hosts = [Host(host_dict) for host_dict in host_dicts]

    def init_templates(self):
        self.login()
        templates = self.template.get()
        for template in templates:
            if template["name"] != "Linux CPU by Zabbix agent active":
                continue
            pdb.set_trace()
        # hosts = self.host.get(filter={"host": host_name}, selectInterfaces=["interfaceid"])

    def raw_create_host(self, dict_request):
        logger.info(f"Raw create Zabbix host: {dict_request['host']}")
        response = self.host.create(**dict_request)
        logger.info(response)
        return response

    def raw_update_host(self, dict_request):
        logger.info(f"Raw update Zabbix host: {dict_request['host']}")
        response = self.host.update(**dict_request)
        logger.info(response)
        return response

    def get_host_id(self, host_src):
        self.init_hosts()
        for host in self.hosts:
            if host.host == host_src.host:
                return host.id
        raise RuntimeError(f"Host not found {host_src.host}")

    def delete_host(self, host_src):
        self.init_hosts()
        for host in self.hosts:
            if host.host == host_src.host:
                self.raw_delete_host(host.generate_delete_request())

    def raw_delete_host(self, request):
        logger.info(f"Raw delete Zabbix host: {request}")
        response = self.host.delete(*request)
        logger.info(response)
        return response

    def provision_host(self, host):
        logger.info(f"Provisioning Zabbix host: {host.name}")
        try:
            response = self.raw_create_host(host.generate_create_request())
        except ZabbixAPIException as exception_instance:
            repr_exception = repr(exception_instance)
            if (
                f'Host with the same name "{host.host}" already exists'
                not in repr_exception
            ):
                raise
            logger.warning(repr_exception)
            host.id = self.get_host_id(host)
            response = self.raw_update_host(host.generate_update_request())
            # self.delete_host(host)
            # response = self.raw_create_host(host.generate_create_request())

        return response


class ZabbixAPIObjectClass(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        """Dynamically create a method (ie: get)"""

        def fn(*args, **kwargs):
            if args and kwargs:
                raise TypeError("Found both args and kwargs")

            return self.parent.do_request(
                "{0}.{1}".format(self.name, attr), args or kwargs
            )["result"]

        return fn
