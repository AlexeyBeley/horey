"""
Grafana api
"""

import json

import requests
from horey.h_logger import get_logger
from horey.grafana_api.grafana_api_configuration_policy import (
    GrafanaAPIConfigurationPolicy,
)
from horey.grafana_api.dashboard import Dashboard
from horey.grafana_api.data_source import DataSource

from horey.grafana_api.folder import Folder
from horey.replacement_engine.replacement_engine import ReplacementEngine

logger = get_logger()


class GrafanaAPI:
    """
    API to work with Grafana 8 API
    """

    def __init__(self, configuration: GrafanaAPIConfigurationPolicy = None):
        self.dashboards = []
        self.folders = []
        self.datasources = []
        self.rule_namespaces = {}

        self.base_address = configuration.server_address
        self.token = configuration.token
        if configuration.token is None:
            self.generate_token(configuration)
        self.replacement_engine = ReplacementEngine()

    def get(self, request_path, old_style=False):
        """
        Execute get call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path, old_style=old_style)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.get(request, headers=headers, timeout=60)
        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        logger.info(f"Response.Raw: '{response.raw}'")
        return response.json()

    def post(self, request_path, data):
        """
        Execute post call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.post(request, data=json.dumps(data), headers=headers, timeout=60)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def put(self, request_path, data):
        """
        Execute post call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.put(request, data=json.dumps(data), headers=headers, timeout=60)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def delete(self, request_path):
        """
        Execute delete call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.delete(request, headers=headers, timeout=60)
        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def provision_organisation(self, org_name):
        """
        Create organisation
        @param org_name:
        @return:
        """
        logger.info(f"Provisioning organisation {org_name}")
        response = self.get("/orgs")
        for org in response:
            if org["name"] == org_name:
                logger.info(f"Found organisation: {response}")
                return org["id"]

        response = self.post("/orgs", {"name": org_name})
        logger.info(f"Provisioned organisation: {response}")
        return response["orgId"]

    def add_user_to_organisation(self, org_id, user):
        """
        Add user to organisation.

        @param org_id:
        @param user:
        @return:
        """
        response = self.get(f"/orgs/{org_id}/users")
        for org in response:
            if org["orgId"] == org_id and org["login"] == user:
                logger.info(f"Found user {user} in organisation: {response}")
                return

        response = self.post(
            f"/orgs/{org_id}/users", {"loginOrEmail": user, "role": "Admin"}
        )
        logger.info(f"Added user {user} to organisation: {response}")

    def generate_token(self, configuration):
        """
        Generate connection token and print it
        org_id = "1"
        response = self.post(f"/user/using/{org_id}", {})
        logger.info(response)
        token_name = "org_1"
        response = self.get("/auth/keys")

        for key in response:
            if key["name"] == token_name:
                self.delete(f"/auth/keys/{key['id']}")
        response = self.get(f"/serviceaccounts/search?perpage=10&page=1&query={token_name}")
        #create: response = self.post("/serviceaccounts", {"name": token_name, "role": "Admin"})
        response = self.post("/auth/keys", {"name": token_name, "role": "Admin"})
        logger.info(response)


        @param configuration:
        @return:
        """
        self.base_address = self.base_address.replace(
            "//", f"//{configuration.user}:{configuration.password}@"
        )
        raise NotImplementedError("Todo: fix the code in docstring")

    def create_request(self, request: str, old_style:bool=False):
        """
        Create full request based on relative request
        @param request:
        @return:
        """
        if request.startswith("/"):
            request = request[1:]

        if old_style:
            return f"{self.base_address}/api/{request}"

        return f"{self.base_address}/apis/{request}"

    def init_datasources(self):
        """
        Init Data sources.
        @return:
        """

        ret = self.get("datasources", old_style=True)
        self.datasources = [DataSource(dict_src) for dict_src in ret]
        return self.datasources

    def init_rule_namespaces(self):
        """
        Init rule namespaces (folders?) and the rules in them.
        @return:
        """
        for name, dict_src in self.get("ruler/grafana/api/v1/rules").items():
            self.rule_namespaces[name] = dict_src

    def provision_dashboard(self, desired: Dashboard):
        """
        Provision dashboard - create or update based on title.
        @param desired:
        @return:
        """

        folder_uid = self.provision_dashboard_folder(desired)
        if folder_uid is not None:
            desired.metadata["annotations"]["grafana.app/folder"] = folder_uid

        self.init_dashboards()
        for current_dashboard in self.dashboards:
            if current_dashboard.spec["title"] == desired.spec["title"]:
                desired.metadata["name"] = current_dashboard.metadata["name"]
                desired.metadata["uid"] = current_dashboard.metadata["uid"]
                return self.update_dashboard_raw(desired.generate_create_request())

        return self.create_dashboard_raw(desired.generate_create_request())

    def provision_dashboard_folder(self, desired_dashboard) -> str:
        """
        Provsision folder by title if does not exist.

        :param desired_dashboard:
        :return:
        """

        if desired_dashboard.metadata["annotations"].get("grafana.app/folder") is None:
            return None

        folders = self.init_folders()
        for folder in folders:
            if folder.spec["title"] == desired_dashboard.metadata["annotations"]["grafana.app/folder"]:
                return folder.metadata["name"]
        raise NotImplementedError("New folder creation")

    def create_dashboard_raw(self, dict_dashboard):
        """
        Create the dashboard from raw dict
        @param dict_dashboard:
        @return: None
        """

        self.post("/dashboard.grafana.app/v1beta1/namespaces/default/dashboards", dict_dashboard)
        logger.info(f"Created Dashboard '{dict_dashboard['spec']['title']}'")

    def update_dashboard_raw(self, dict_dashboard):
        """
        Create the dashboard from raw dict
        @param dict_dashboard:
        @return: None
        """

        self.put(f"/dashboard.grafana.app/v1beta1/namespaces/default/dashboards/{dict_dashboard['metadata']['name']}", dict_dashboard)
        logger.info(f"Updated Dashboard '{dict_dashboard['spec']['title']}'")
        return True

    def create_rule_raw(self, dict_request, namespace):
        """
        Create the dashboard from raw dict
        @param dict_dashboard:
        @return: None
        """
        self.post(f"ruler/grafana/api/v1/rules/{namespace}", dict_request)
        logger.info(f"Created Alerts '{'a'}'")

    def provision_datasource(self, datasource: DataSource):
        """
        Provision data source
        @param datasource:
        @return: None
        """
        try:
            self.post("datasources", datasource.generate_create_request())
        except Exception as exception_instance:
            if "data source with the same name already exists" in repr(
                exception_instance
            ):
                self.put(
                    f"datasources/{datasource.id}", datasource.generate_create_request()
                )

    @staticmethod
    def get_next_refid(ref_id):
        """
        Generate next Ref ID. i.e. None, A, B...
        @param ref_id:
        @return:
        """
        if ref_id is None:
            return "A"

        if ref_id == "Z":
            raise NotImplementedError()

        return chr(ord(ref_id) + 1)

    def init_dashboards(self):
        """
        Init dashboards
        @return:
        """

        ret = self.get("dashboard.grafana.app/v1beta1/namespaces/default/dashboards")
        self.dashboards = [Dashboard(dict_src) for dict_src in ret["items"]]
        return self.dashboards

    def init_folders(self) -> list[Folder]:
        """
        Init dashboards
        @return:
        """

        ret = self.get("folder.grafana.app/v1beta1/namespaces/default/folders")
        self.folders = [Folder(dict_src) for dict_src in ret["items"]]
        return self.folders
