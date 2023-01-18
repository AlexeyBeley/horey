"""
Working with kapacitor API

"""
import json

import requests
from horey.h_logger import get_logger

logger = get_logger()


class Task:
    """
    Kapacitor task
    """
    def __init__(self, dict_src):
        self.dict_src = dict_src
        self.id = dict_src["id"]


class KapacitorAPI:
    """
    Kapacitor toolset
    """

    def __init__(self, configuration):
        self.configuration = configuration
        self.tasks = []
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json-rpc",
                "User-Agent": "python/pyzabbix",
                "Cache-Control": "no-cache",
            }
        )

    def init_tasks(self):
        """
        Init all the tasks
        :return:
        """

        tasks = []
        while True:
            response = self.get(f"tasks?offset={len(tasks)}&limit=100")
            tasks += response["tasks"]
            logger.info(f'Fetched {len(response["tasks"])} tasks, total count fetched until now: {len(tasks)}')
            if len(response["tasks"]) == 0:
                break

        self.tasks = [Task(dict_src) for dict_src in tasks]

    def get(self, request_params):
        """
        GET request.

        :param request_params:
        :return:
        """
        response = self.session.get(self.generate_request(request_params), timeout=60)
        return response.json()

    def generate_request(self, request_params):
        """
        Generate request from address, API url and request params.

        :param request_params:
        :return:
        """

        return self.configuration.server_address+"/kapacitor/v1/" + request_params.strip("/")

    def cache_tasks(self, file_path):
        """
        Write tasks to file.

        :param file_path:
        :return:
        """

        self.init_tasks()
        tasks_source = [task.dict_src for task in self.tasks]
        with open(file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(json.dumps(tasks_source))
