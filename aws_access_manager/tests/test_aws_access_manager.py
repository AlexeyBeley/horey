"""
Testing AWS Cleaner

"""
import os
import pytest

from horey.aws_access_manager.aws_access_manager import AWSAccessManager
from horey.common_utils.common_utils import CommonUtils
from horey.aws_access_manager.aws_access_manager_configuration_policy import (
    AWSAccessManagerConfigurationPolicy,
)
from horey.aws_api.base_entities.region import Region

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "access_manager", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring

@pytest.fixture(name="configuration")
def fixture_configuration():
    """
    Fixture used as a base config.

    :return:
    """

    _configuration = AWSAccessManagerConfigurationPolicy()
    _configuration.aws_api_accounts = ["test1"]
    ignore_dir_path = os.path.join( os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore")
    _configuration.managed_accounts_file_path = os.path.abspath(
        os.path.join(
            ignore_dir_path,
            "accounts",
            "aws_managed_accounts.py"
        )
    )
    _configuration.cache_dir = os.path.join(ignore_dir_path, "access_manager", "cache")

    return _configuration


@pytest.mark.done
def test_get_user_assume_roles(configuration: AWSAccessManagerConfigurationPolicy):
    ret = AWSAccessManager(configuration).get_user_assume_roles(mock_values["get_user_faces_user_name"])
    assert len(ret) > 0


@pytest.mark.done
def test_get_iam_role_lambdas(configuration: AWSAccessManagerConfigurationPolicy):
    roles = AWSAccessManager(configuration).get_user_assume_roles(mock_values["get_user_faces_user_name"])
    for role in roles:
        ret = AWSAccessManager(configuration).get_iam_role_lambdas(Region.get_region("us-west-2"), role)
        assert isinstance(ret, list)

@pytest.mark.skip
def test_provision_iam_role_lambdas_assumable_roles(configuration: AWSAccessManagerConfigurationPolicy):
    roles = AWSAccessManager(configuration).get_user_assume_roles(mock_values["get_user_faces_user_name"])
    for role in roles:
        ret = AWSAccessManager(configuration).provision_iam_role_lambdas_assumable_roles(Region.get_region("us-west-2"), role)
        assert isinstance(ret, list)

@pytest.mark.todo
def test_get_role_assume_roles(configuration: AWSAccessManagerConfigurationPolicy):
    roles = AWSAccessManager(configuration).get_user_assume_roles(mock_values["get_user_faces_user_name"])
    for role in roles:
        ret = AWSAccessManager(configuration).get_role_assume_roles(role)
        assert isinstance(ret, list)

@pytest.mark.todo
def test_generate_user_aws_api_accounts(configuration: AWSAccessManagerConfigurationPolicy):
    aws_access_manager = AWSAccessManager(configuration)
    roles = aws_access_manager.get_user_assume_roles(mock_values["get_user_faces_user_name"])
    aws_access_key_id = mock_values["get_user_faces_aws_access_key_id"]
    aws_secret_access_key = mock_values["get_user_faces_aws_secret_access_key"]
    accounts = aws_access_manager.generate_user_aws_api_accounts(aws_access_key_id, aws_secret_access_key, roles)
    assert isinstance(accounts, list)


@pytest.mark.done
def test_generate_user_security_domain_tree(configuration: AWSAccessManagerConfigurationPolicy):
    access_manager = AWSAccessManager(configuration)
    user = access_manager.aws_api.find_user_by_name(mock_values["get_user_faces_user_name"])
    tree = access_manager.generate_user_security_domain_tree(user)
    tree.print()
    assert tree is not None

@pytest.mark.done
def test_generate_users_security_domain_tree(configuration: AWSAccessManagerConfigurationPolicy):
    ret = AWSAccessManager(configuration).generate_users_security_domain_tree()
    assert ret is not None

@pytest.mark.wip
def test_generate_users_security_domain_graphs(configuration: AWSAccessManagerConfigurationPolicy):
    ret = AWSAccessManager(configuration).generate_users_security_domain_graphs()
    assert ret is not None
