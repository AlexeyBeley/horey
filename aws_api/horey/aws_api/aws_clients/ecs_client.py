"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client


class ECSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ecs"
        super().__init__(client_name)

    def register_task_definition(self, request_dict):
        for response in self.execute(self.client.register_task_definition, "taskDefinition", filters_req=request_dict):
            pdb.set_trace()

    def create_cluster(self, request_dict):
        for response in self.execute(self.client.create_cluster, "cluster", filters_req=request_dict):
            pdb.set_trace()

    def run_task(self, request_dict):
        for response in self.execute(self.client.run_task, "tasks", filters_req=request_dict):
            return response
