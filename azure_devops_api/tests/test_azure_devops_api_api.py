"""
Testing chronograf api
"""
import os
import pytest

from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import (
    AzureDevopsAPIConfigurationPolicy,
)

configuration = AzureDevopsAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "azure_devops_api_configuration_values.py",
    )
)
configuration.init_from_file()

azure_devops_api = AzureDevopsAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_init_backlogs():
    azure_devops_api.init_backlogs()


if __name__ == "__main__":
    test_init_backlogs()
