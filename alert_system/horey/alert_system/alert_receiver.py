import pdb

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy


logger = get_logger()


class AlertReceiver:
    def __init__(self, configuration):
        self.configuration = configuration

    def provision(self):
        pdb.set_trace()
        self.provision_sns()
        self.provision_lambda()


    def provision_sns(self):
        pdb.set_trace()

    def provision_lambda(self):
        pdb.set_trace()

