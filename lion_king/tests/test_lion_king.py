"""
Test async orchestrator
"""
import os.path

import pytest

from horey.lion_king.lion_king import LionKing
from horey.lion_king.lion_king_configuration_policy import LionKingConfigurationPolicy

# pylint: disable = missing-function-docstring

configuration_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "lion_king", "lion_king_configuration.py"))

@pytest.mark.done
def test_provision_vpc():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    vpc = lion_king.provision_vpc()
    assert vpc.id


@pytest.mark.done
def test_provision_subnets():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    subnets = lion_king.provision_subnets()
    assert len(subnets) > 0

@pytest.mark.done
def test_provision_ecr_repository():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    repo = lion_king.provision_ecr_repository()
    assert repo.arn

@pytest.mark.wip
def test_login_to_ecr():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.login_to_ecr()

@pytest.mark.todo
def test_build_and_upload():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.build_and_upload()


@pytest.mark.done
def test_dispose():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.dispose()
