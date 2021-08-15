"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSTaskDefinition(AwsObject):
    """
    AWS AutoScalingGroup class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "taskDefinitionArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "containerDefinitions": self.init_default_attr,
            "family": self.init_default_attr,
            "taskRoleArn": self.init_default_attr,
            "executionRoleArn": self.init_default_attr,
            "revision": self.init_default_attr,
            "volumes": self.init_default_attr,
            "requiresAttributes": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "compatibilities": self.init_default_attr,
            "requiresCompatibilities": self.init_default_attr,
            "cpu": self.init_default_attr,
            "memory": self.init_default_attr,
            "registeredAt": self.init_default_attr,
            "registeredBy": self.init_default_attr,
            "status": self.init_default_attr,
            "networkMode": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        init_options = {
            "taskDefinitionArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "containerDefinitions": self.init_default_attr,
            "family": self.init_default_attr,
            "taskRoleArn": self.init_default_attr,
            "executionRoleArn": self.init_default_attr,
            "revision": self.init_default_attr,
            "volumes": self.init_default_attr,
            "requiresAttributes": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "compatibilities": self.init_default_attr,
            "requiresCompatibilities": self.init_default_attr,
            "cpu": self.init_default_attr,
            "memory": self.init_default_attr,
            "registeredAt": self.init_default_attr,
            "registeredBy": self.init_default_attr,
            "status": self.init_default_attr,
            "networkMode": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        response = client.register_task_definition(
    family='string',
    taskRoleArn='string',
    executionRoleArn='string',
    networkMode='bridge'|'host'|'awsvpc'|'none',
    containerDefinitions=[
        {
            'name': 'string',
            'image': 'string',
            'repositoryCredentials': {
                'credentialsParameter': 'string'
            },
            'cpu': 123,
            'memory': 123,
            'memoryReservation': 123,
            'links': [
                'string',
            ],
            'portMappings': [
                {
                    'containerPort': 123,
                    'hostPort': 123,
                    'protocol': 'tcp'|'udp'
                },
            ],
            'essential': True|False,
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
                    'readOnly': True|False
                },
            ],
            'volumesFrom': [
                {
                    'sourceContainer': 'string',
                    'readOnly': True|False
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
                            'read'|'write'|'mknod',
                        ]
                    },
                ],
                'initProcessEnabled': True|False,
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
                    'condition': 'START'|'COMPLETE'|'SUCCESS'|'HEALTHY'
                },
            ],
            'startTimeout': 123,
            'stopTimeout': 123,
            'hostname': 'string',
            'user': 'string',
            'workingDirectory': 'string',
            'disableNetworking': True|False,
            'privileged': True|False,
            'readonlyRootFilesystem': True|False,
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
            'interactive': True|False,
            'pseudoTerminal': True|False,
            'dockerLabels': {
                'string': 'string'
            },
            'ulimits': [
                {
                    'name': 'core'|'cpu'|'data'|'fsize'|'locks'|'memlock'|'msgqueue'|'nice'|'nofile'|'nproc'|'rss'|'rtprio'|'rttime'|'sigpending'|'stack',
                    'softLimit': 123,
                    'hardLimit': 123
                },
            ],
            'logConfiguration': {
                'logDriver': 'json-file'|'syslog'|'journald'|'gelf'|'fluentd'|'awslogs'|'splunk'|'awsfirelens',
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
                    'type': 'GPU'|'InferenceAccelerator'
                },
            ],
            'firelensConfiguration': {
                'type': 'fluentd'|'fluentbit',
                'options': {
                    'string': 'string'
                }
            }
        },
    ],
    volumes=[
        {
            'name': 'string',
            'host': {
                'sourcePath': 'string'
            },
            'dockerVolumeConfiguration': {
                'scope': 'task'|'shared',
                'autoprovision': True|False,
                'driver': 'string',
                'driverOpts': {
                    'string': 'string'
                },
                'labels': {
                    'string': 'string'
                }
            },
            'efsVolumeConfiguration': {
                'fileSystemId': 'string',
                'rootDirectory': 'string',
                'transitEncryption': 'ENABLED'|'DISABLED',
                'transitEncryptionPort': 123,
                'authorizationConfig': {
                    'accessPointId': 'string',
                    'iam': 'ENABLED'|'DISABLED'
                }
            },
            'fsxWindowsFileServerVolumeConfiguration': {
                'fileSystemId': 'string',
                'rootDirectory': 'string',
                'authorizationConfig': {
                    'credentialsParameter': 'string',
                    'domain': 'string'
                }
            }
        },
    ],
    placementConstraints=[
        {
            'type': 'memberOf',
            'expression': 'string'
        },
    ],
    requiresCompatibilities=[
        'EC2'|'FARGATE'|'EXTERNAL',
    ],
    cpu='string',
    memory='string',
    tags=[
        {
            'key': 'string',
            'value': 'string'
        },
    ],
    pidMode='host'|'task',
    ipcMode='host'|'task'|'none',
    proxyConfiguration={
        'type': 'APPMESH',
        'containerName': 'string',
        'properties': [
            {
                'name': 'string',
                'value': 'string'
            },
        ]
    },
    inferenceAccelerators=[
        {
            'deviceName': 'string',
            'deviceType': 'string'
        },
    ],
    ephemeralStorage={
        'sizeInGiB': 123
    }
)
        """
        request = dict()
        request["name"] = self.name
        request["containerDefinitions"] = self.container_definitions
        request["tags"] = self.tags
        request["family"] = self.family
        request["taskRoleArn"] = self.task_role_arn
        request["executionRoleArn"] = self.execution_role_arn
        request["requiresCompatibilities"] = ["EC2"]

        request["cpu"] = self.cpu
        request["memory"] = self.memory

        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise NotImplementedError()
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
