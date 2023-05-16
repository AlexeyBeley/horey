"""
Security report generation
"""

import os
from datetime import date
import pytest
from horey.aws_api.aws_api import AWSAPI

from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy


logger = get_logger()
configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "aws_api_configuration_values.py",
    )
)
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)

# pylint: disable = missing-function-docstring


@pytest.mark.skip(reason="IAM policies cleanup will be enabled explicitly")
def test_report():
    report_file_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "ignore",
            f"security_report_{str(date.today())}.txt",
    ))
    tb_ret = aws_api.generate_security_reports(report_file_path)
    assert tb_ret is not None


if __name__ == "__main__":
    test_report()
