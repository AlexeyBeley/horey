"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json
import pdb

import requests
from horey.h_logger import get_logger
from horey.grafana_api.grafana_api_configuration_policy import GrafanaAPIConfigurationPolicy
from horey.grafana_api.dashboard import Dashboard
from horey.grafana_api.folder import Folder

logger = get_logger()


class GrafanaAPI:
    def __init__(self, configuration: GrafanaAPIConfigurationPolicy = None):
        self.dashboards = []
        self.folders = []
        self.datasources = []

        self.base_address = configuration.server_address
        self.token = configuration.token
        if configuration.token is None:
            self.generate_token(configuration)

    def get(self, request_path):
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
        response = self.get(f"/orgs/{org_id}/users")
        for org in response:
            if org["orgId"] == org_id and org["login"] == user:
                logger.info(f"Found user {user} in organisation: {response}")
                return

        response = self.post(f"/orgs/{org_id}/users", {"loginOrEmail": user, "role": "Admin"})
        logger.info(f"Added user {user} to organisation: {response}")

    def generate_token(self, configuration):
        org_name = "apiorg"
        self.base_address = self.base_address.replace("//", f"//{configuration.user}:{configuration.password}@")

        #org_id = self.provision_organisation(org_name)
        #self.add_user_to_organisation(org_id, configuration.user)
        org_id = "1"
        response = self.post(f"/user/using/{org_id}", {})
        logger.info(response)
        token_name = "org_1"
        response = self.get(f"/auth/keys")

        for key in response:
            if key["name"] == token_name:
                self.delete(f"/auth/keys/{key['id']}")

        response = self.post(f"/auth/keys", {"name": token_name, "role": "Admin"})
        logger.info(response)

    def create_request(self, request: str):
        if request.startswith("/"):
            request = request[1:]

        return f"{self.base_address}/api/{request}"

    def init_folders_and_dashboards(self):
        for dash_data in self.get("search"):
            if dash_data["type"] == "dash-folder":
                folder = self.init_folder(dash_data)
                self.folders.append(folder)
            elif dash_data["type"] == "dash-db":
                dashboard = self.init_dashboard(dash_data)
                self.dashboards.append(dashboard)
            else:
                raise RuntimeError(dash_data)

    def init_datasources(self):
        pdb.set_trace()
        for dash_data in self.get("datasources"):
            if dash_data["type"] == "dash-folder":
                folder = self.init_folder(dash_data)
                self.folders.append(folder)
            elif dash_data["type"] == "dash-db":
                dashboard = self.init_dashboard(dash_data)
                self.dashboards.append(dashboard)
            else:
                raise RuntimeError(dash_data)

    def init_folder(self, dict_src):
        ret = Folder(dict_src)
        return ret

    def init_dashboard(self, dict_src):
        dashboard = Dashboard(dict_src)
        ret = self.get(f"/dashboards/uid/{dashboard.uid}")
        dashboard.update_full_info({"meta": ret["meta"], **ret["dashboard"]})
        return dashboard

    def provision_dashboard(self, dashboard):
        self.post("dashboards/db", dashboard.generate_create_request())

    def provision_datasource(self, datasource):
        self.post("datasources", datasource.generate_create_request())
