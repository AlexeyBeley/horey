"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json
import pdb

import requests
from horey.h_logger import get_logger
from horey.grafana_api.grafana_api_configuration_policy import GrafanaAPIConfigurationPolicy

logger = get_logger()

class GrafanaAPI:
    def __init__(self, configuration: GrafanaAPIConfigurationPolicy = None):
        self.base_address = configuration.server_address
        self.version = "v1"
        self.sources = []
        self.kapacitors = []
        self.rules = []
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

        org_id = self.provision_organisation(org_name)

        self.add_user_to_organisation(org_id, configuration.user)

        response = self.post(f"/user/using/{org_id}", {})
        logger.info(response)

        token_name = "apikeycurl"
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

    def init_kapacitors(self):
        """
        http://127.0.0.1:8888/chronograf/v1/sources/{id}/kapacitors
        @return:
        """
        if not self.sources:
            self.init_sources()
        logger.info(f"Initializing grafana kapacitors")

        objs = []
        for source in self.sources:
            response = self.get(f"sources/{source.id}/kapacitors")

            for dict_src in response["kapacitors"]:
                obj = Kapacitor(dict_src)
                objs.append(obj)

        self.kapacitors = objs

    def init_rules(self):
        """
        http://127.0.0.1:8888/chronograf/v1/sources/{id}/kapacitors/{kapa_id}/rules

        @return:
        """
        if not self.kapacitors:
            self.init_kapacitors()
        objs = []
        for kapacitor in self.kapacitors:
            response = self.get(kapacitor.links["rules"], is_link=True)

            for dict_src in response["rules"]:
                obj = Rule(dict_src)
                objs.append(obj)

        self.rules = objs

    def provision_dashboard(self, dashboard):
        pdb.set_trace()
        self.post("dashboards", dashboard.dict_src)
