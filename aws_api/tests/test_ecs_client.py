import os
import sys
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "/Users/alexeybe/private/IP/ip")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/base_entities")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/aws_clients")

from ecs_client import ECSClient
import ignore_me
import logging

logger = logging.Logger(__name__)
from aws_account import AWSAccount

tested_account = ignore_me.acc_default
AWSAccount.set_aws_account(tested_account)

cache_base_path = os.path.join(os.path.expanduser("~"), f"private/aws_api/ignore/cache_objects_{tested_account.name}")


def test_init_ecs_client():
    assert isinstance(ECSClient(), ECSClient)


CONTAINER_NAME = "test-container-name"
IMAGE_URL = ".dkr.ecr.us-east-1.amazonaws.com/my-web-app:latest"
CPU_SIZE = 512
MEMORY_SIZE = 1024
CONTAINER_PORT = 8080
HOST_PORT = 8080
TASK_DEFINITION_FAMILY = "task-definition-family"

dict_request_base = {"family": None,
                     "taskRoleArn": "",
                     "executionRoleArn": "",
                     "networkMode": "none",
                     "containerDefinitions": [
                         {
                             "name": CONTAINER_NAME,
                             "image": IMAGE_URL,
                             'repositoryCredentials': {
                                 'credentialsParameter': 'string'
                             },
                             'cpu': CPU_SIZE,
                             'memory': MEMORY_SIZE,
                             'memoryReservation': MEMORY_SIZE,
                             'links': [
                                 'string',
                             ],
                             'portMappings': [
                                 {
                                     'containerPort': CONTAINER_PORT,
                                     'hostPort': HOST_PORT,
                                     'protocol': 'tcp'
                                 },
                             ],
                             'essential': False,
                             'entryPoint': [
                                 'string',
                             ],
                             'command': [
                                 'string',
                             ],
                             'environment': [
                                 {
                                     'name': 'string',
                                     'value': 'string'
                                 },
                             ],
                             'environmentFiles': [
                                 {
                                     'value': 'string',
                                     'type': 's3'
                                 },
                             ],
                             'mountPoints': [
                                 {
                                     'sourceVolume': 'string',
                                     'containerPath': 'string',
                                     'readOnly': False
                                 },
                             ],
                             'volumesFrom': [
                                 {
                                     'sourceContainer': 'string',
                                     'readOnly': False
                                 },
                             ],
                             'linuxParameters': {
                                 'capabilities': {
                                     'add': [
                                         'string',
                                     ],
                                     'drop': [
                                         'string',
                                     ]
                                 },
                                 'devices': [
                                     {
                                         'hostPath': 'string',
                                         'containerPath': 'string',
                                         'permissions': [
                                             'write',
                                         ]
                                     },
                                 ],
                                 'initProcessEnabled': False,
                                 'sharedMemorySize': 123,
                                 'tmpfs': [
                                     {
                                         'containerPath': 'string',
                                         'size': 123,
                                         'mountOptions': [
                                             'string',
                                         ]
                                     },
                                 ],
                                 'maxSwap': 123,
                                 'swappiness': 123
                             },
                             'secrets': [
                                 {
                                     'name': 'string',
                                     'valueFrom': 'string'
                                 },
                             ],
                             'dependsOn': [
                                 {
                                     'containerName': 'string',
                                     'condition': 'START'
                                 },
                             ],
                             'startTimeout': 123,
                             'stopTimeout': 123,
                             'hostname': 'string',
                             'user': 'string',
                             'workingDirectory': 'string',
                             'disableNetworking': False,
                             'privileged': False,
                             'readonlyRootFilesystem': True,
                             'dnsServers': [
                                 'string',
                             ],
                             'dnsSearchDomains': [
                                 'string',
                             ],
                             'extraHosts': [
                                 {
                                     'hostname': 'string',
                                     'ipAddress': 'string'
                                 },
                             ],
                             'dockerSecurityOptions': [
                                 'string',
                             ],
                             'interactive': False,
                             'pseudoTerminal': False,
                             'dockerLabels': {
                                 'string': 'string'
                             },
                             'ulimits': [
                                 {
                                     'name': 'core',
                                     'softLimit': 123,
                                     'hardLimit': 123
                                 },
                             ],
                             'logConfiguration': {
                                 'logDriver': 'json-file',
                                 'options': {
                                     'string': 'string'
                                 },
                                 'secretOptions': [
                                     {
                                         'name': 'string',
                                         'valueFrom': 'string'
                                     },
                                 ]
                             },
                             'healthCheck': {
                                 'command': [
                                     'string',
                                 ],
                                 'interval': 123,
                                 'timeout': 123,
                                 'retries': 123,
                                 'startPeriod': 123
                             },
                             'systemControls': [
                                 {
                                     'namespace': 'string',
                                     'value': 'string'
                                 },
                             ],
                             'resourceRequirements': [
                                 {
                                     'value': 'string',
                                     'type': 'InferenceAccelerator'
                                 },
                             ],
                             'firelensConfiguration': {
                                 'type': 'fluentd',
                                 'options': {
                                     'string': 'string'
                                 }
                             }
                         },
                     ]
                     }
EXECUTION_ROLE_ARN = "arn:aws:iam:::role/HoreyEcsExecutionRole1"
dict_register_td_request = {"family": TASK_DEFINITION_FAMILY,
                            "executionRoleArn": EXECUTION_ROLE_ARN,
                            "requiresCompatibilities": ["FARGATE"],
                            "networkMode": "awsvpc",
                            'cpu': str(CPU_SIZE),
                            'memory': str(MEMORY_SIZE),
                            "containerDefinitions": [
                                {
                                    "name": CONTAINER_NAME,
                                    "image": IMAGE_URL,
                                    'portMappings': [
                                        {
                                            'containerPort': CONTAINER_PORT,
                                            'hostPort': HOST_PORT,
                                            'protocol': 'tcp'
                                        },
                                    ],
                                    'essential': True
                                },
                            ]
                            }


def test_register_task_definition():
    client = ECSClient()
    client.register_task_definition(dict_register_td_request)


CLUSTER_NAME = "my-cluster-name"
dict_create_cluster_request = {"clusterName": CLUSTER_NAME,
                               "capacityProviders": ["FARGATE"]
                               }


def test_create_cluster():
    client = ECSClient()
    client.create_cluster(dict_create_cluster_request)


ALLOWED_SUBNETS = []
SECURITY_GROUPS = []
dict_run_task_request = {"cluster": CLUSTER_NAME, "taskDefinition": TASK_DEFINITION_FAMILY,
                         "launchType": "FARGATE",
                         "networkConfiguration": {
                             "awsvpcConfiguration": {
                                 "subnets": ALLOWED_SUBNETS,
                                 "securityGroups": SECURITY_GROUPS,
                                 "assignPublicIp": "ENABLED"
                             }
                         }
                         }


def test_run_task():
    client = ECSClient()
    client.run_task(dict_run_task_request)


"""
def     
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)
        aws_api.init_s3_buckets(full_information=False)

        aws_api.cleanup_report_s3_buckets()

    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)
"""

if __name__ == "__main__":
    # test_register_task_definition()
    test_run_task()
