"""
Working with eks env.

"""

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.eks_cluster import EKSCluster


class K8S:
    """
    aws eks update-kubeconfig --region us-west-2 --name test-aws-example
    """
    def __init__(self):
        self.aws_api = AWSAPI()

    def provision_role(self, name):
        """
        Role Creation

        :param name:
        :return:
        """

        iam_role = IamRole({})
        iam_role.description = "alert_system lambda role"
        iam_role.name = name
        iam_role.max_session_duration = 12 * 60 * 60
        policy_src = """{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }"""
        iam_role.assume_role_policy_document = policy_src
        policy = IamPolicy({})
        policy.arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
        iam_role.policies.append(policy)
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def get_cluster_login_credentials(self, cluster_name, region):
        """
        Find the cluster and retrieve the login credentials.

        :param cluster_name:
        :return:
        """

        cluster = EKSCluster({"name": cluster_name})
        cluster.region = region
        self.aws_api.eks_client.update_cluster_info(cluster)
        return cluster.endpoint, cluster.certificate_authority["data"]