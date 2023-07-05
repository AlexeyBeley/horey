"""
ELB V2 client tests.

"""
import os

from horey.aws_api.aws_clients.elbv2_client import ELBV2Client
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

accounts_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "ignore",
        "aws_api_managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

client = ELBV2Client()

# pylint: disable= missing-function-docstring


def test_init_client():
    assert isinstance(ELBV2Client(), ELBV2Client)


def provision_load_balancer():
    load_balancer = LoadBalancer({})
    load_balancer.region = Region.get_region("us-west-2")

    load_balancer.name = "lb-test"
    load_balancer.subnets = mock_values["load_balancer_test_provision_subnets"]
    load_balancer.scheme = "internet-facing"

    load_balancer.tags = [{
        "Key": "Name",
        "Value": load_balancer.name
    }]
    load_balancer.type = "application"
    load_balancer.ip_address_type = "ipv4"

    client.provision_load_balancer(load_balancer)
    return load_balancer


def test_provision_load_balancer():
    load_balancer = provision_load_balancer()

    assert load_balancer.arn is not None


def test_dispose_load_balancer():
    load_balancer = LoadBalancer({})
    load_balancer.region = Region.get_region("us-west-2")

    load_balancer.name = "lb-test"
    client.dispose_load_balancer(load_balancer)


def test_provision_listener():
    load_balancer = provision_load_balancer()
    listener = LoadBalancer.Listener({})
    listener.protocol = "HTTPS"
    listener.ssl_policy = "ELBSecurityPolicy-FS-1-2-2019-08"

    listener.port = 443
    listener.certificates = [
        {
            "CertificateArn": mock_values["cert_1_arn"]
        }]

    listener.default_actions = [
        {
            "Type": "redirect",
            "Order": 1,
            "RedirectConfig": {
                "Protocol": "HTTPS",
                "Port": "444",
                "Host": "#{host}",
                "Path": "/#{path}",
                "Query": "#{query}",
                "StatusCode": "HTTP_301"
            }
        }
    ]

    listener.load_balancer_arn = load_balancer.arn
    listener.region = load_balancer.region

    client.provision_load_balancer_listener(listener)
    client.dispose_listener_raw(listener.generate_dispose_request())


def test_provision_listener_multiple_certs():
    load_balancer = provision_load_balancer()
    listener = LoadBalancer.Listener({})
    listener.protocol = "HTTPS"
    listener.ssl_policy = "ELBSecurityPolicy-FS-1-2-2019-08"

    listener.port = 443
    listener.certificates = [
        {
            "CertificateArn": mock_values["cert_1_arn"]
        },
        {
            "CertificateArn": mock_values["cert_2_arn"]
        }
    ]

    listener.default_actions = [
        {
            "Type": "redirect",
            "Order": 1,
            "RedirectConfig": {
                "Protocol": "HTTPS",
                "Port": "444",
                "Host": "#{host}",
                "Path": "/#{path}",
                "Query": "#{query}",
                "StatusCode": "HTTP_301"
            }
        }
    ]

    listener.load_balancer_arn = load_balancer.arn
    listener.region = load_balancer.region

    client.provision_load_balancer_listener(listener)
    client.dispose_listener_raw(listener.generate_dispose_request())


def test_set_rule_priorities_raw():
    """

    {"RuleArn": "", "Priority": 1},

    :return:
    """

    request = {"RulePriorities": [
        {"RuleArn": "arn", "Priority": 2},
    ]}

    AWSAccount.set_aws_region(Region.get_region("us-west-2"))
    ret = client.set_rule_priorities_raw(request)
    print(ret)


if __name__ == "__main__":
    # test_provision_load_balancer()
    # test_provision_listener()
    # test_provision_listener_multiple_certs()
    # test_dispose_load_balancer()
    test_set_rule_priorities_raw()
