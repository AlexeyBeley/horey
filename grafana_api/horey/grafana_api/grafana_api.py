"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json

import requests
from horey.h_logger import get_logger
from horey.grafana_api.grafana_api_configuration_policy import GrafanaAPIConfigurationPolicy
from horey.grafana_api.dashboard import Dashboard
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

    def get(self, request_path):
        """
        Execute get call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.get(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
            )
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

        response = requests.post(
            request, data=json.dumps(data),
            headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
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

        response = requests.delete(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
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

        response = self.post(f"/orgs/{org_id}/users", {"loginOrEmail": user, "role": "Admin"})
        logger.info(f"Added user {user} to organisation: {response}")

    def generate_token(self, configuration):
        """
        Generate connection token and print it

        @param configuration:
        @return:
        """
        self.base_address = self.base_address.replace("//", f"//{configuration.user}:{configuration.password}@")

        org_id = "1"
        response = self.post(f"/user/using/{org_id}", {})
        logger.info(response)
        token_name = "org_1"
        response = self.get("/auth/keys")

        for key in response:
            if key["name"] == token_name:
                self.delete(f"/auth/keys/{key['id']}")

        response = self.post("/auth/keys", {"name": token_name, "role": "Admin"})
        logger.info(response)

    def create_request(self, request: str):
        """
        Create full request based on relative request
        @param request:
        @return:
        """
        if request.startswith("/"):
            request = request[1:]

        return f"{self.base_address}/api/{request}"

    def init_folders_and_dashboards(self):
        """
        Init folders and dashboards
        @return:
        """
        for dash_data in self.get("search"):
            if dash_data["type"] == "dash-folder":
                folder = Folder(dash_data)
                self.folders.append(folder)
            elif dash_data["type"] == "dash-db":
                dashboard = self.generate_dashboard(dash_data)
                self.dashboards.append(dashboard)
            else:
                raise RuntimeError(dash_data)

    def init_datasources(self):
        """
        Init Data sources.
        @return:
        """
        for dict_src in self.get("datasources"):
            self.datasources.append(dict_src)

    def init_rule_namespaces(self):
        """
        Init rule namespaces (folders?) and the rules in them.
        @return:
        """
        for name, dict_src in self.get("ruler/grafana/api/v1/rules").items():
            self.rule_namespaces[name] = dict_src

    def init_folders(self):
        """
        Init dashboards' folders
        @return:
        """
        for dict_src in self.get("folders"):
            self.folders.append(Folder(dict_src))

    def generate_dashboard(self, dict_src):
        """
        Init object from raw server response
        @param dict_src:
        @return:
        """
        dashboard = Dashboard(dict_src)
        ret = self.get(f"/dashboards/uid/{dashboard.uid}")
        dashboard.update_full_info({"meta": ret["meta"], **ret["dashboard"]})
        return dashboard

    def provision_dashboard(self, dashboard):
        """
        Provision dashboard - create or update based on title.
        @param dashboard:
        @return:
        """
        self.create_dashboard_raw(dashboard.generate_create_request())

    def create_dashboard_raw(self, dict_dashboard):
        """
        Create the dashboard from raw dict
        @param dict_dashboard:
        @return: None
        """
        self.post("dashboards/db", dict_dashboard)
        logger.info(f"Created Dashboard '{dict_dashboard['dashboard']['title']}'")

    def provision_datasource(self, datasource):
        """
        Provision data source
        @param datasource:
        @return: None
        """
        self.post("datasources", datasource.generate_create_request())
