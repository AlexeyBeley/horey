"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""

import os
import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate
from horey.aws_api.aws_services_entities.ses_identity import SESIdentity
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.key_pair import KeyPair
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import (
    LambdaEventSourceMapping,
)
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup


configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)

logger = get_logger(
    configuration_file_full_path=configuration_values_file_full_path
)

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "accounts",
        "aws_api_configuration_values.py",
    )
)


configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable = missing-function-docstring

@pytest.mark.done
def test_add_managed_region():
    aws_api.add_managed_region(Region.get_region("us-west-2"))


@pytest.mark.todo
def test_provision_certificate():
    cert = ACMCertificate({})
    cert.region = Region.get_region("us-east-1")
    cert.domain_name = "front.horey.com"
    cert.validation_method = "DNS"
    cert.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": cert.domain_name.replace("*", "star")},
    ]

    hosted_zone_name = "horey.com"
    aws_api.provision_acm_certificate(cert, hosted_zone_name)

    assert cert.status == "ISSUED"


@pytest.mark.todo
def test_provision_sesv2_domain_email_identity():
    email_identity = SESIdentity({})
    email_identity.name = mock_values["email_identity.name"]
    email_identity.region = Region.get_region("us-west-2")
    email_identity.tags = [{"Key": "name", "Value": "value"}]
    aws_api.provision_sesv2_domain_email_identity(email_identity)

    assert email_identity.verified_for_sending_status == "ISSUED"


@pytest.mark.todo
def test_provision_aws_lambda_from_filelist():
    aws_lambda = AWSLambda({})
    aws_lambda.region = Region.get_region("us-west-2")
    aws_lambda.name = "horey-test-lambda"
    aws_lambda.role = mock_values["lambda:execution_role"]
    aws_lambda.handler = "lambda_test.lambda_handler"
    aws_lambda.runtime = "python3.8"
    aws_lambda.tags = {"lvl": "tst", "name": "horey-test"}
    aws_lambda.reserved_concurrent_executions = 2
    aws_lambda.timeout = 300
    aws_lambda.memory_size = 512

    files_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        for filename in ["lambda_test.py", "lambda_test_2.py"]
    ]
    aws_api.provision_aws_lambda_from_filelist(aws_lambda, files_paths, update_code=True)

    assert aws_lambda.state == "Active"


@pytest.mark.todo
def test_provision_lambda_event_source_mapping():
    event_mapping = LambdaEventSourceMapping({})
    event_mapping.region = Region.get_region("us-west-2")
    event_mapping.function_identification = "horey-test-lambda"
    event_mapping.event_source_arn = mock_values[
        "lambda_event_source_mapping:event_source_arn"
    ]
    event_mapping.enabled = True

    aws_api.provision_lambda_event_source_mapping(event_mapping)

    assert event_mapping.state == "Enabled"


@pytest.mark.todo
def test_find_cloudfront_distributions():
    aws_api.init_cloudfront_distributions()
    ret = aws_api.find_cloudfront_distributions(tags=[{"Key": "test_tag", "Value": "test_value"}])
    assert ret is not None


@pytest.mark.todo
def test_provision_key_pair():
    key_pair = KeyPair({})
    key_pair.name = "test-default-type-key"
    key_pair.tags = [{
        "Key": "Name",
        "Value": key_pair.name
    }]
    key_pair.region = Region.get_region("us-west-2")
    aws_api.provision_key_pair(key_pair, save_to_secrets_manager=True, secrets_manager_region="us-west-2")


@pytest.mark.todo
def test_get_secret_value():
    ret = aws_api.get_secret_value("test", ignore_missing=True)
    assert ret is None


@pytest.mark.todo
def test_provision_generated_ssh_key():
    owner_email = "test_horey@gmail.com"
    output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.key")
    aws_api.provision_generated_ssh_key(output_file_path, owner_email, "us-west-2")

@pytest.mark.todo
def test_renew_ecs_cluster_container_instances():
    ecs_cluster = ECSCluster({})
    ecs_cluster.region = Region.get_region("us-west-2")
    ecs_cluster.name = mock_values["renew_ecs_cluster.name"]
    aws_api.renew_ecs_cluster_container_instances(ecs_cluster)

security_group_name = "test_sg"
vpc_name = "test_vpc"
def provision_vpc():
    vpc= VPC({})
    vpc.region = Region.get_region("us-west-2")
    vpc.cidr_block = "10.255.0.0/16"
    vpc.tags = [{
    "Key": "Name",
    "Value": vpc_name}]

    aws_api.provision_vpc(vpc)
    return vpc

@pytest.mark.done
def test_provision_vpc():
    vpc = provision_vpc()
    assert vpc.id is not None


@pytest.mark.done
def test_get_security_group_by_vpc_and_name():
    vpc = provision_vpc()
    aws_api.get_security_group_by_vpc_and_name(vpc, security_group_name)


@pytest.mark.done
def test_dispose_vpc():
    vpc = provision_vpc()
    aws_api.ec2_client.dispose_vpc(vpc)
    assert vpc.id is not None


@pytest.mark.done
def test_find_route_table_by_subnet():
    region = Region.get_region("us-west-2")
    aws_api.init_subnets(region=region)
    subnet = aws_api.subnets[0]
    ret = aws_api.find_route_table_by_subnet(subnet)
    assert ret is not None


@pytest.mark.wip
def test_detach_and_delete_ecs_container_instances():
    current_ec2_instance_ids = []
    region = Region.get_region("us-east-1")
    auto_scaling_group_arn = ""

    auto_scaling_group = AutoScalingGroup({})
    auto_scaling_group.region = region
    auto_scaling_group.arn = auto_scaling_group_arn
    aws_api.autoscaling_client.update_auto_scaling_group_information(auto_scaling_group)

    aws_api.autoscaling_client.detach_instances(auto_scaling_group, current_ec2_instance_ids, decrement=True)

    # terminate old instances
    for current_ec2_instance_id in current_ec2_instance_ids:
        ec2_instance = EC2Instance({})
        ec2_instance.region = region
        ec2_instance.id = current_ec2_instance_id
        aws_api.ec2_client.dispose_instance(ec2_instance)
