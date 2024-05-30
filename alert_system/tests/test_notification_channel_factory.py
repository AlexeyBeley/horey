"""
Notification channel factory
"""
import json
import os.path
import sys
import pytest
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.alert_system.lambda_package.notification_channels.notification_channel_factory import \
    NotificationChannelFactory
from horey.alert_system.lambda_package.notification_channels.notification_channel_echo import NotificationChannelEcho
from horey.alert_system.lambda_package.notification_channels.notification_channel_ses import NotificationChannelSES
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.notification_channels.notification_channel_slack import NotificationChannelSlack
import fixtures


# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_load_notification_channel_echo():
    factory = NotificationChannelFactory()
    notification_channel = factory.load_notification_channel(sys.modules[NotificationChannelEcho.__module__].__file__)
    assert notification_channel


@pytest.mark.wip
def test_create_ses_configs_file():
    aws_api = AWSAPI()
    region = Region.get_region("us-west-2")
    identities = aws_api.sesv2_client.get_all_email_identities(region)
    for identity in identities:
        if identity.identity_type == "DOMAIN":
            break
    else:
        raise ValueError("No domain identity found")

    receipt_rule_sets = aws_api.ses_client.yield_receipt_rule_sets(region=region)
    for rule_set in receipt_rule_sets:
        for rule in rule_set.rules:
            if not rule["Enabled"]:
                continue
            if not rule.get("Recipients"):
                continue
            rule_recipient = rule["Recipients"][0]
            break
        else:
            continue
        break
    else:
        raise ValueError("No Recipients found")

    config_dict = {"region": "us-west-2",
                   "src_email": f"alert_system_test@{identity.name}",
                   "routing_tag_to_email_mapping": {"test": rule_recipient},
                   "alert_system_monitoring_destination": rule_recipient}

    test_notification_channels_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "notification_channels"))
    with open(os.path.join(test_notification_channels_dir, "notification_channel_ses_config.json"),
              "w") as file_handler:
        json.dump(config_dict, file_handler, indent=4)


@pytest.mark.todo
def test_load_notification_channels():
    test_notification_channels_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "notification_channels"))

    factory = NotificationChannelFactory()
    configuration = AlertSystemConfigurationPolicy()
    configuration.notification_channels = [sys.modules[NotificationChannelEcho.__module__].__file__,
                                           os.path.join(test_notification_channels_dir,
                                                        "notification_channel_ses_initializer.py")
                                           ]

    notification_channel = factory.load_notification_channels(configuration)
    assert notification_channel
