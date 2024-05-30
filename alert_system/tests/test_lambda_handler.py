import os

from horey.alert_system.lambda_package.lambda_handler import lambda_handler
import pytest
from fixtures import fixture_lambda_package_alert_system_config_file
from common import ses_events


print(fixture_lambda_package_alert_system_config_file)


@pytest.mark.wip
@pytest.mark.parametrize("ses_event", ses_events)
def test_lambda_handler(lambda_package_alert_system_config_file, ses_event):
    event_handler = lambda_handler(ses_event, None)
    assert event_handler["statusCode"] == 200

