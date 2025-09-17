"""
Shamelessly stolen from:
https://github.com/lukecyca/pyzabbix
https://www.zabbix.com/documentation/current/en/manual/api/reference/host

"""

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


class ZabbixAPI:
    """
    Main class

    """

    def __init__(self, configuration: ZabbixAPIConfigurationPolicy = None):
        if configuration.session is not None:
            self.session = configuration.session
        else:
            self.session = requests.Session()

        # Default headers for all requests
        self.session.headers.update(
            {
                "Content-Type": "application/json-rpc",
                "User-Agent": "python/pyzabbix"
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

    def check_authentication(self):
        """Convenience method for calling user.checkAuthentication of the current session"""
        return self.user.checkAuthentication(sessionid=self.auth)

    @property
    def is_authenticated(self):
        """
        Checks if auth works.

        :return:
        """

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
        """
        Standard.

        :return:
        """

        return self.apiinfo.version()

    def login(self):
        """
        Get tmp auth
        :return:
        """

        try:
            return self.lgged_in
        except AttributeError:
            pass

        ret = self.post("user.login", params={"username": "Admin", "password": self.configuration.password})
        self.session.headers.update(
            {
                "Content-Type": "application/json-rpc",
                "User-Agent": "python/pyzabbix",
                "Authorization": f"Bearer {ret}"
            }
        )

        setattr(self, "lgged_in", True)

    def post(self, method, params=None):
        """
        Standard get.
        :param params:
        :return:
        """
        self.id += 1

        request_json = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.id,
        }
        response = self.session.post(
            self.url, data=json.dumps(request_json), timeout=self.timeout
        )
        response.raise_for_status()
        dict_response = json.loads(response.text)

        if "error" in dict_response:
            raise RuntimeError(f"Request {method=} returned {dict_response.get('error')}")

        return dict_response["result"]

    def do_request(self, method, params=None):
        """
        Perform post request.

        :param method:
        :param params:
        :return:
        """

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

    def init_hosts(self):
        """
        Fetch hosts.

        :return:
        """

        self.login()

        host_dicts = self.post("host.get", params={"selectHostGroups": "extend", "selectInterfaces": [
            "interfaceid",
            "ip",
            "type",
            "main",
            "useip",
            "dns",
            "port",
        ], "selectParentTemplates": ["templateid", "name"]})

        self.hosts = [Host(host_dict) for host_dict in host_dicts]

    def init_templates(self):
        """
        Fetch templates
        :return:
        """

        self.login()
        return self.template.get()

    def raw_create_host(self, dict_request):
        """
        Create host using prepared request.

        :param dict_request:
        :return:
        """

        logger.info(f"Raw create Zabbix host: {dict_request['host']}")
        response = self.post("host.create", params=dict_request)
        logger.info(response)
        return response

    def raw_update_host(self, dict_request):
        """
        Update host using ready request.

        :param dict_request:
        :return:
        """

        logger.info(f"Raw update Zabbix host: {dict_request['hostid']}")
        response = self.post("host.update", params=dict_request)
        logger.info(response)
        return response

    def get_host_id(self, host_src):
        """
        Find host id by hostname.

        :param host_src:
        :return:
        """

        self.init_hosts()
        for host in self.hosts:
            if host.host == host_src.host:
                return host.id
        raise RuntimeError(f"Host not found {host_src.host}")

    def delete_host(self, host_src):
        """
        Remove host by hostname.

        :param host_src:
        :return:
        """

        self.init_hosts()
        for host in self.hosts:
            if host.host == host_src.host:
                self.raw_delete_host(host.generate_delete_request())
                return True
        return True

    def raw_delete_host(self, request):
        """
        Delete host using ready request.

        :param request:
        :return:
        """

        logger.info(f"Raw delete Zabbix host: {request}")
        response = self.host.delete(*request)
        logger.info(response)
        return response

    def provision_host(self, desired_host: Host):
        """
        Create or update a host.

        :param desired_host:
        :return:
        """
        logger.info(f"Provisioning Zabbix host: {desired_host.name}")
        self.init_hosts()
        for existing_host in self.hosts:
            if existing_host.name == desired_host.name:
                response = self.raw_update_host(desired_host.generate_update_request())
                break
        else:
            response = self.raw_create_host(desired_host.generate_create_request())

        return response

    def init_graphs(self):
        """
        Fetch hosts.

        :return:
        """

        self.login()

        # todo: refactor to standard get
        ret = self.do_request("graph.get", params={
            "output": "extend",
            "sortfield": "name"
        })

        return ret["result"]


class ZabbixAPIObjectClass(object):
    """
    Base object class
    """

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
