import pdb
import sys

sys.path.insert(0, "/Users/alexey.beley/private/horey/aws_api")

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.jenkins_manager.jenkins_configuration_policy import JenkinsConfigurationPolicy
from horey.jenkins_manager.jenkins_manager import JenkinsManager


class JenkinsDeployer:
    """
    ssh -i ~/.ssh/jenkins-key.pem -o StrictHostKeyChecking=no  ubuntu@ip.a.d.dr
    """

    def __init__(self, configuration):
        aws_api_conf = AWSAPIConfigurationPolicy()
        aws_api_conf.configuration_file_full_path = configuration.aws_api_configuration_values_file_path
        aws_api_conf.init_from_file()
        self.aws_api = AWSAPI(configuration=aws_api_conf)

        jenkins_conf = JenkinsConfigurationPolicy()
        jenkins_conf.configuration_file_full_path = configuration.jenkins_manager_configuration_values_file_path
        jenkins_conf.init_from_file()
        self.jenkins_manager = JenkinsManager(configuration=jenkins_conf)

        self.jenkins_ec2_instance_type = configuration.jenkins_ec2_instance_type
        self.ssh_master_access_key_name = "jenkins-master-access-key"
        self.ssh_agent_access_key_name = "jenkins-agent-access-key"

        self.jenkins_mater_iam_role_name = "role-jenkins-master"
        self.jenkins_mater_iam_role_name = "policy-jenkins-master-spot-fleet-access"
        self.public_subnet_id = ""
        self.private_subnet_id = ""
        self.jenkins_master_security_group_name = ""
        self.ssh_agent_security_group_name = ""

    def deploy_infrastructure(self):
        security_group_id = self.deploy_master_infra()
        self.deploy_agent_infra(security_group_id)

    def deploy_agent_infra(self, security_group_id):
        launch_template_id = self.deploy_agent_launch_template(security_group_id)
        self.deploy_agent_spot_fleet(launch_template_id)

    def agent_spot_fleet(self):
        return {
            "SpotFleetRequestConfig": {
            "ReplaceUnhealthyInstances": True,
            "Type": "maintain",
            "IamFleetRole": f"arn:aws:iam::{ACCOUNT_ID}:role/spot-fleet_requester-role",
            "LaunchTemplateConfigs": [
                {
                    'LaunchTemplateSpecification': {
                        'LaunchTemplateName': 'launch_template_jenkins_agent',
                        "Version": "$Latest"
                    }
                },
            ],
            "TargetCapacity": 1,
            'TagSpecifications': [
                {
                    'ResourceType': 'spot-fleet-request',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'spot-fleet-request-agents-tmp'
                        },
                        {
                            'Key': 'env_name',
                            'Value': 'production'
                        },
                        {
                            'Key': 'env_level',
                            'Value': 'production'
                        },
                    ]
                },
            ]
        }
        }

    def deploy_agent_spot_fleet(self, deploy_agent_spot_fleet):
        dict_req = self.agent_spot_fleet()
        spot_fleet = self.aws_api.ec2_client.request_spot_fleet(dict_req)
        print(spot_fleet)

    def agent_launch_template(self, security_group_id):
        return {
            "LaunchTemplateName": "launch_template_jenkins_agent",
            "LaunchTemplateData": {
                "InstanceInitiatedShutdownBehavior": 'terminate',
                "NetworkInterfaces": [
                    {
                        'AssociatePublicIpAddress': False,
                        'DeleteOnTermination': True,
                        'DeviceIndex': 0,
                        'Groups': [
                            security_group_id,
                        ],
                        'Ipv6AddressCount': 0,
                        'SubnetId': SUBNET_ID,
                        'InterfaceType': 'interface',
                        'NetworkCardIndex': 0
                    },
                ],
                "CreditSpecification": {
                    'CpuCredits': 'unlimited'
                },
                "BlockDeviceMappings": [
                    {
                        'DeviceName': '/dev/sda1',
                        'Ebs': {
                            'DeleteOnTermination': True,
                            'VolumeSize': 20,
                            'VolumeType': 'standard',
                        },
                    }
                ],
                "ImageId": IMAGE_ID,
                "InstanceType": 't2.micro',
                "KeyName": 'jenkins-key',
                "Monitoring": {
                    'Enabled': True
                },
                "TagSpecifications": [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'jenkins-agent-tmp'
                            },
                            {
                                'Key': 'env_level',
                                'Value': 'production'
                            },
                            {
                                'Key': 'env_name',
                                'Value': 'production'
                            }
                        ]
                    },
                ],
                "IamInstanceProfile": {
                    'Name': 'service-role-jenkins'
                }
            },
            "TagSpecifications": [
                {
                    'ResourceType': 'launch-template',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'launch_template_jenkins-agent-tmp'
                        },
                        {
                            'Key': 'env_level',
                            'Value': 'production'
                        },
                        {
                            'Key': 'env_name',
                            'Value': 'production'
                        }
                    ]
                },
            ],
        }

    def deploy_agent_launch_template(self, security_group_id):
        dict_req = self.agent_launch_template(security_group_id)
        launch_template = self.aws_api.ec2_client.create_launch_template(dict_req)
        launch_template_id = launch_template["LaunchTemplateId"]
        return launch_template_id

    def deploy_master_infra(self):
        security_group_agent_id = self.deploy_infrastructure_security_groups()
        return security_group_agent_id
        self.deploy_key_pairs()
        self.deploy_infrastructure_master_role()
        self.deploy_infrastructure_master_instance()

    def role_master(self):
        assume_role_policy = """{
        "Version": "2012-10-17",
        "Statement": [
        {
        "Effect": "Allow",
        "Principal": {
        "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
        }
        ]
        }"""

        return {
            "RoleName": 'role-jenkins-master-tmp',
            "AssumeRolePolicyDocument": assume_role_policy,
            "Tags": [
                {
                    'Key': 'Name',
                    'Value': 'role-jenkins-master-tmp'
                },
                {
                    'Key': 'env_name',
                    'Value': 'production'
                },
                {
                    'Key': 'env_level',
                    'Value': 'production'
                },
            ]
        }

    def policies_master(self):
        lst_ret = []
        lst_ret.append({"PolicyName": "spot-fleet", "PolicyDocument": """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSpotFleetInstances",
                "ec2:ModifySpotFleetRequest",
                "ec2:CreateTags",
                "ec2:DescribeRegions",
                "ec2:DescribeInstances",
                "ec2:TerminateInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeSpotFleetRequests"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:UpdateAutoScalingGroup"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:ListInstanceProfiles",
                "iam:ListRoles",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}"""}
                       )
        lst_ret.append({"PolicyName": "packer", "PolicyDocument": """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AttachVolume",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CopyImage",
                "ec2:CreateImage",
                "ec2:CreateKeypair",
                "ec2:CreateSecurityGroup",
                "ec2:CreateSnapshot",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:DeleteKeyPair",
                "ec2:DeleteSecurityGroup",
                "ec2:DeleteSnapshot",
                "ec2:DeleteVolume",
                "ec2:DeregisterImage",
                "ec2:DescribeImageAttribute",
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeRegions",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSnapshots",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "ec2:DescribeVolumes",
                "ec2:DetachVolume",
                "ec2:GetPasswordData",
                "ec2:ModifyImageAttribute",
                "ec2:ModifyInstanceAttribute",
                "ec2:ModifySnapshotAttribute",
                "ec2:RegisterImage",
                "ec2:RunInstances",
                "ec2:StopInstances",
                "ec2:TerminateInstances"
            ],
            "Resource": "*"
        }
    ]
        }"""})
        return lst_ret

    def deploy_infrastructure_master_role(self):
        dict_req = self.role_master()
        response = self.aws_api.iam_client.create_role(dict_req)
        lst_policy_requests = self.policies_master()
        for policy_request in lst_policy_requests:
            policy_request["RoleName"] = "role-jenkins-master-tmp"
            response = self.aws_api.iam_client.attach_role_inline_policy(policy_request)
            print(response)

    def deploy_infrastructure_security_groups(self):
        sg_id = self.deploy_infrastructure_master_security_group()
        sg_agent_id = self.deploy_infrastructure_agents_security_group(sg_id)
        return sg_agent_id

    def deploy_infrastructure_master_security_group(self):
        security_group = {
            "Description": "Jenkins master security_group",
            "GroupName": "security_group_jenkins_master_tmp",
            "VpcId": VPC_ID,
            "TagSpecifications": [
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'security_group_jenkins_master'
                        },
                    ]
                },
            ],
        }

        sg_id = self.aws_api.ec2_client.raw_create_security_group(security_group)
        input_ports_request = {
            "GroupId": sg_id,
            "IpPermissions": [
                {'IpProtocol': 'tcp',
                 'FromPort': 8080,
                 'ToPort': 8080,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            ]}
        self.aws_api.ec2_client.authorize_security_group_ingress(input_ports_request)
        return sg_id

    def deploy_infrastructure_agents_security_group(self, sg_id_master):
        security_group = {
            "Description": "Jenkins agent security_group",
            "GroupName": "security_group_jenkins_agent",
            "VpcId": VPC_ID,
            "TagSpecifications": [
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'security_group_jenkins_agent'
                        },
                    ]
                },
            ],
        }

        sg_agent_id = self.aws_api.ec2_client.raw_create_security_group(security_group)
        input_ports_request = {
            "GroupId": sg_agent_id,
            "IpPermissions": [
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 "UserIdGroupPairs": [
                     {
                         "GroupId": sg_id_master,
                     }
                 ]
                 },
            ]}
        #pdb.set_trace()
        self.aws_api.ec2_client.authorize_security_group_ingress(input_ports_request)
        return sg_agent_id

    def instance_master(self):
        return {
            "DisableApiTermination": True,
            "InstanceInitiatedShutdownBehavior": 'stop',
            "NetworkInterfaces": [
                {
                    'AssociatePublicIpAddress': True,
                    'DeleteOnTermination': True,
                    'DeviceIndex': 0,
                    'Groups': [
                        SEC_GROUP,
                    ],
                    'Ipv6AddressCount': 0,
                    'SubnetId': SUBNET,
                    'InterfaceType': 'interface',
                    'NetworkCardIndex': 0
                },
            ],
            "CreditSpecification": {
                'CpuCredits': 'unlimited'
            },
            "BlockDeviceMappings": [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 20,
                        'VolumeType': 'standard',
                    },
                },
                {
                    'DeviceName': '/dev/sdb',
                    'Ebs': {
                        'DeleteOnTermination': False,
                        'VolumeSize': 40,
                        'VolumeType': 'standard',
                    },
                },
                {
                    'DeviceName': '/dev/sdc',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 20,
                        'VolumeType': 'standard',
                    },
                },
            ],
            "ImageId": AMI_ID,
            "InstanceType": 't2.micro',
            "KeyName": 'jenkins-key',
            "Monitoring": {
                'Enabled': True
            },
            "TagSpecifications": [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'jenkins-master-tmp'
                        },
                        {
                            'Key': 'env_level',
                            'Value': 'production'
                        },
                        {
                            'Key': 'env_name',
                            'Value': 'production'
                        },

                    ]
                },
            ],
            "IamInstanceProfile": {
                'Name': 'service-role-jenkins'
            },
            "MaxCount": 1,
            "MinCount": 1
        }

    def deploy_infrastructure_master_instance(self):
        dict_req = self.instance_master()
        self.aws_api.ec2_client.create_instance(dict_req)

    def deploy_key_pairs(self):
        key_master_req = {
            "KeyName": 'jenkins_master_key',
            "TagSpecifications": [
                {
                    'ResourceType': 'key-pair',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'jenkins_master_key'
                        },
                    ]
                },
            ]}
        self.aws_api.ec2_client.create_key_pair(key_master_req)

        key_agent_req = {
            "KeyName": 'jenkins_agent_key',
            "TagSpecifications": [
                {
                    'ResourceType': 'key-pair',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'jenkins_agent_key'
                        },
                    ]
                },
            ]}
        self.aws_api.ec2_client.create_key_pair(key_agent_req)
