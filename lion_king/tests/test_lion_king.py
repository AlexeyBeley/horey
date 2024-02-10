"""
Test async orchestrator
"""
import os.path

import pytest

from horey.lion_king.lion_king import LionKing
from horey.lion_king.lion_king_configuration_policy import LionKingConfigurationPolicy

# pylint: disable = missing-function-docstring

configuration_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "lion_king", "lion_king_configuration.py"))

@pytest.mark.wip
def test_provision_vpc():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    vpc = lion_king.provision_vpc()
    assert vpc.id

@pytest.mark.wip
def test_dispose():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.dispose()
