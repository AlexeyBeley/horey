"""
Test aws k8s client.

"""

import json
import os

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.k8s import K8S
from horey.aws_api.aws_services_entities.eks_fargate_profile import EKSFargateProfile
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_role import IamRole

logger = get_logger()


definition_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "step_definition.json"
    )
)

# pylint: disable= missing-function-docstring

k8s = K8S()
cluster_name = "test-aws-example"


def test_get_cluster_login_credentials():
    """
    Base init check.

    @return:
    """
    region = Region.get_region("us-west-2")
    k8s.get_cluster_login_credentials(cluster_name, region)


def test_provision_eks_pod_execution_policy():
    """
    Provision policy used by pod execution role

    :return:
    """

    policy = IamPolicy({})
    policy.document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage"
                ],
                "Resource": "arn:aws:ecr:us-west-2::repository/*"
            }
        ]
    }
    policy.document = json.dumps(policy.document)
    policy.name = "policy-test-pod-execution"
    policy.description = "EKS POD execution policy"
    policy.tags = [{
        "Key": "Name",
        "Value": policy.name
    }]
    k8s.aws_api.provision_iam_policy(policy)
    return policy


def test_provision_eks_pod_execution_role():
    """
    https://docs.aws.amazon.com/eks/latest/userguide/pod-execution-role.html#create-pod-execution-role
    :return:
    """
    policy = test_provision_eks_pod_execution_policy()
    iam_role = IamRole({})
    iam_role.description = "EKS POD execution role"
    iam_role.name = "role-test-pod-execution"
    iam_role.max_session_duration = 12 * 60 * 60
    iam_role.tags = [{
        "Key": "Name",
        "Value": iam_role.name
    }]
    iam_role.assume_role_policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Condition": {
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:eks:us-west-2:{account_id}:fargateprofile/{cluster_name}/*"
                    }
                },
                "Principal": {
                    "Service": "eks-fargate-pods.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
    iam_role.policies.append(policy)
    k8s.aws_api.provision_iam_role(iam_role)
    return iam_role


def test_provision_fargate_profile():
    """
    https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html
    --cluster test-aws-example \
    --region us-west-2 \
    --name alb-sample-app \
    --namespace game-2048
    :return:
    """

    _k8s = K8S()
    eks_fargate_profile = EKSFargateProfile({})
    eks_fargate_profile.region = Region.get_region("us-west-2")
    eks_fargate_profile.name = "alb-sample-app"
    eks_fargate_profile.cluster_name = "test-aws-example"
    role = test_provision_eks_pod_execution_role()
    eks_fargate_profile.pod_execution_role_arn = role.arn
    eks_fargate_profile.tags = [{"Key": "Name", "Value": eks_fargate_profile.name}]
    eks_fargate_profile.selectors=[{
        "namespace": "game-2048",
        "labels": {
        "service_name": "test_label"
    }}
    ]
    _k8s.aws_api.eks_client.provision_fargate_profile(eks_fargate_profile)
    assert eks_fargate_profile.arn is not None


def test_dispose_fargate_profile():
    """
    https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html

    :return:
    """

    _k8s = K8S()
    eks_fargate_profile = EKSFargateProfile({})
    eks_fargate_profile.region = Region.get_region("us-west-2")
    eks_fargate_profile.name = "alb-sample-app"
    eks_fargate_profile.cluster_name = "test-aws-example"
    _k8s.aws_api.eks_client.dispose_fargate_profile(eks_fargate_profile)
