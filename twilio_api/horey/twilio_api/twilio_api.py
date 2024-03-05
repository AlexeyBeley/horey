"""
Twilio client test.

"""
from twilio.rest import Client
from horey.h_logger import get_logger
from horey.twilio_api.twilio_api_configuration_policy import TwilioAPIConfigurationPolicy


logger = get_logger()


class TwilioAPI:
    """
    API to work with Grafana 8 API
    """

    def __init__(self, configuration: TwilioAPIConfigurationPolicy = None):
        self.employees = None

        self.token = configuration.token
        self.configuration = configuration
        self.client = Client(self.configuration.account_sid, self.configuration.token)

    def send_whatsapp(self):
        """
        Send a message

        :return:
        """
        response = self.client.messages.create(
                              body='Hello there!',
                              from_='whatsapp:+14155238886',
                              to='whatsapp:+14155238886'
                          )
        return response
