import os
import pdb

import pytest

from horey.aws_api.aws_api import AWSAPI

from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy


logger = get_logger()
configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_values.py")
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)


@pytest.mark.skip(reason="IAM policies cleanup will be enabled explicitly")
def test_report():
    aws_api.generate_security_reports()
    pdb.set_trace()


if __name__ == "__main__":
    test_report()