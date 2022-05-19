"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json
import pdb

import requests
from horey.h_logger import get_logger
from horey.influxdb_api.influxdb_api_configuration_policy import InfluxDBAPIConfigurationPolicy

logger = get_logger()


class InfluxDBObject:
    def __init__(self, dict_src):
        self.dict_src = dict_src
        for key, value in dict_src.items():
            setattr(self, key, value)


class Source(InfluxDBObject):
    def __init__(self, dict_src):
        super().__init__(dict_src)


class Kapacitor(InfluxDBObject):
    def __init__(self, dict_src):
        super().__init__(dict_src)


class Rule(InfluxDBObject):
    def __init__(self, dict_src):
        super().__init__(dict_src)


class InfluxDBAPI:
    def __init__(self, configuration: InfluxDBAPIConfigurationPolicy = None):
        self.base_address = configuration.server_address
        self.version = "v1"
        self.sources = []
        self.kapacitors = []
        self.rules = []

    def init_sources(self):
        logger.info(f"Initializing influxdb sources")
        response = self.get("sources")

        objs = []
        for dict_src in response["sources"]:
            obj = Source(dict_src)
            objs.append(obj)

        self.sources = objs

    def get(self, request_path, is_link=False):
        request = self.create_request(request_path, is_link=is_link)
        response = requests.get(
            request,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to influxdb api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def post(self, request_path, data, is_link=False):
        request = self.create_request(request_path, is_link=is_link)
        response = requests.post(
            request, data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to influxdb api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def create_request(self, request, is_link=False):
        """
        http://127.0.0.1:8888/chronograf/v1/sources
        """
        if is_link:
            return f"{self.base_address}{request}"

        return f"{self.base_address}/chronograf/{self.version}/{request}"

    def init_kapacitors(self):
        """
        http://127.0.0.1:8888/chronograf/v1/sources/{id}/kapacitors
        @return:
        """
        if not self.sources:
            self.init_sources()
        logger.info(f"Initializing influxdb kapacitors")

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
