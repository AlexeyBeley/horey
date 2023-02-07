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
        self.status = dict_src["status"]
        self.script = dict_src["script"]
        self.dbrps = dict_src["dbrps"]
        self.type = dict_src["type"]

    def generate_provision_request(self):
        """
        Generate

        :return:
        """

        return {
            "id": self.id,
            "type": self.type,
            "dbrps": self.dbrps,
            "script": self.script,
            "status": self.status
        }


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
        return self.tasks

    def get(self, request_params):
        """
        GET request.

        :param request_params:
        :return:
        """
        response = self.session.get(self.generate_request(request_params), timeout=60)
        return response.json()

    def delete(self, request_params):
        """
         DELETE request.

        :param request_params:
        :return:
        """

        logger.info(f"Deleting task: {request_params}")

        response = self.session.delete(self.generate_request(request_params), timeout=60)
        if response.status_code not in [204]:
            raise RuntimeError(response.text)

    def post(self, request_params, data):
        """
        POST request.

        :param request_params:
        :param data:
        :return:
        """
        response = self.session.post(self.generate_request(request_params), data=json.dumps(data), timeout=60)
        if response.status_code not in [200]:
            breakpoint()
            raise RuntimeError(f"Request: params- {request_params}, data- {data}. Response: {response.text}")
        return response.json()

    def patch(self, request_params, data):
        """
        POST request.

        :param request_params:
        :param data:
        :return:
        """
        response = self.session.patch(self.generate_request(request_params), data=json.dumps(data), timeout=60)
        if response.status_code not in [200]:
            raise RuntimeError(f"request_params: {request_params}, data: {data}, response: {response.text}")
        return response.json()

    def generate_request(self, request_params):
        """
        Generate request from address, API url and request params.

        :param request_params:
        :return:
        """

        return self.configuration.server_address + "/kapacitor/v1/" + request_params.strip("/")

    def cache_tasks(self, file_path):
        """
        Write tasks to file.

        :param file_path:
        :return:
        """

        tasks_source = [task.dict_src for task in self.init_tasks()]
        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(tasks_source, file_handler)

    def provision_from_cache(self, file_path):
        """
        Write tasks to file.

        :param file_path:
        :return:
        """
        with open(file_path, "r", encoding="utf-8") as file_handler:
            tasks_source = json.load(file_handler)

        for task_src in tasks_source:
            #self.delete_task(Task(task_src))
            #continue
            task_src["status"] = "disabled"
            self.provision_task(Task(task_src))

    def delete_task(self, task):
        """
        Delete task

        :return:
        """

        self.delete(f"tasks/{task.id}")

    def provision_task(self, task: Task):
        """
        Provision task.

        :param task:
        :return:
        """

        logger.info(f"Provisioning task: {task.id}")

        return self.post("tasks", task.generate_provision_request())

    def disable_all_tasks(self):
        """
        Disable all tasks

        :return:
        """

        for task in self.init_tasks():
            self.patch(f"tasks/{task.id}", {"status": "disabled"})
            logger.info(f"Disabled task: {task.id}")

    def enable_all_tasks(self):
        """
        Disable all tasks

        :return:
        """

        for task in self.init_tasks():
            self.patch(f"tasks/{task.id}", {"status": "enabled"})
            logger.info(f"Enabled task: {task.id}")
