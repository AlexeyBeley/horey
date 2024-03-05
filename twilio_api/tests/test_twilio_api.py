"""
Testing grafana API
"""
import os
import pytest

from horey.twilio_api.twilio_api import TwilioAPI
from horey.twilio_api.twilio_api_configuration_policy import TwilioAPIConfigurationPolicy


ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "twilio"
)

configuration = TwilioAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(ignore_dir_path, "twilio_api_configuration_values.py")
)
configuration.init_from_file()

# pylint: disable=missing-function-docstring


@pytest.mark.wip
def test_init_twilio_api():
    _twilio_api = TwilioAPI(configuration=configuration)
    assert isinstance(_twilio_api, TwilioAPI)


@pytest.mark.wip
def test_send_whatsapp():
    _twilio_api = TwilioAPI(configuration=configuration)
    assert _twilio_api.send_whatsapp()
