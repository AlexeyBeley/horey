"""
Testing AWS Cleaner

"""
import os
import time

import pytest

from horey.aws_access_manager.aws_access_manager import AWSAccessManager
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils
from horey.aws_access_manager.aws_access_manager_configuration_policy import (
    AWSAccessManagerConfigurationPolicy,
)
from horey.h_logger import get_logger

logger = get_logger()

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "access_manager", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

configuration = AWSAccessManagerConfigurationPolicy()
configuration.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
configuration.aws_api_account_name = "iam_manager"
configuration.managed_accounts_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..",
        "ignore",
        "accounts",
        "aws_managed_accounts.py",
    )
)

access_manager = AWSAccessManager(configuration)
user = access_manager.aws_api.find_user_by_name(mock_values["get_user_faces_user_name"])
roles = access_manager.get_user_assume_roles(user.name)


def cleanup_user_credentials(original_aws_api_account=None, credentials=None):
    """
    Delete the newly generates user credentials.

    :return:
    """
    original_aws_api_account = original_aws_api_account or RuntimeData.original_aws_api_account
    credentials = credentials or RuntimeData.credentials

    AWSAccount.set_aws_account(original_aws_api_account)
    request = {"UserName": user.name, "AccessKeyId": credentials["AccessKeyId"]}
    return access_manager.aws_api.iam_client.delete_access_key_raw(request)


class RuntimeData:
    """
    RuntimeData data class.
    """

    credentials = access_manager.aws_api.iam_client.create_access_key(user)
    original_aws_api_account = AWSAccount.get_aws_account()
    try:
        aws_api_accounts = access_manager.generate_user_aws_api_accounts(credentials["AccessKeyId"],
                                                                         credentials["SecretAccessKey"], roles)
        # This block is needed for credentials propagation
        AWSAccount.set_aws_account(aws_api_accounts[0])
        start_perf_counter = time.perf_counter()
        for i in range(60 * 10):
            try:
                access_manager.aws_api.sts_client.get_account()
                break
            except Exception as inst_error:
                if "InvalidClientTokenId" not in repr(inst_error):
                    raise
                time.sleep(0.1)
        logger.info(f"Token propagation took: {time.perf_counter() - start_perf_counter}")

        AWSAccount.set_aws_account(original_aws_api_account)

    except Exception as inst_error:
        logger.exception(inst_error)
        cleanup_user_credentials(original_aws_api_account=original_aws_api_account, credentials=credentials)
        raise


@pytest.mark.done
@pytest.mark.parametrize("aws_api_account", RuntimeData.aws_api_accounts)
def test_user_access_list_secrets(aws_api_account):
    """
    Test list secrets

    :param aws_api_account:
    :return:
    """

    AWSAccount.set_aws_account(aws_api_account)

    expected_error_string = r"An error occurred \(AccessDeniedException\) when calling the ListSecrets operation: User: .* " \
                            r"is not authorized to perform: secretsmanager:ListSecrets because no identity-based policy allows " \
                            r"the secretsmanager:ListSecrets action"
    AWSAccount.set_aws_region(Region.get_region("us-east-1"))
    with pytest.raises(Exception, match=expected_error_string):
        for _ in access_manager.aws_api.secretsmanager_client.yield_secrets_raw():
            break

@pytest.mark.wip
@pytest.mark.parametrize("aws_api_account", RuntimeData.aws_api_accounts)
def test_user_access_get_secret(aws_api_account):
    """
    Test list secrets

    :param aws_api_account:
    :return:
    """

    AWSAccount.set_aws_account(aws_api_account)

    expected_error_string = r"An error occurred \(AccessDeniedException\) when calling the ListSecrets operation: User: .* " \
                            r"is not authorized to perform: secretsmanager:ListSecrets because no identity-based policy allows " \
                            r"the secretsmanager:ListSecrets action"
    breakpoint()
    AWSAccount.set_aws_region(Region.get_region("us-east-1"))
    with pytest.raises(Exception, match=expected_error_string):
        access_manager.aws_api.secretsmanager_client.get_secret_value("test_secret_name")

@pytest.mark.done
@pytest.mark.parametrize("aws_api_account", RuntimeData.aws_api_accounts)
def test_user_access_stop_server(aws_api_account):
    """
    Test server stop
    expected_error_string = "An error occurred (DryRunOperation) when calling the TerminateInstances operation: Request would have succeeded, but DryRun flag is set."

    :param aws_api_account:
    :return:
    """
    protected_instance_id = mock_values["credentials_test_dispose_protected_instance_id"]
    request = {"InstanceIds": [protected_instance_id],
               "DryRun": True
               }

    AWSAccount.set_aws_account(aws_api_account)
    AWSAccount.set_aws_region(Region.get_region("us-east-1"))

    expected_error_string = r"An error occurred \(UnauthorizedOperation\) when calling the TerminateInstances operation:" \
                            r" You are not authorized to perform this operation. User: .* is not authorized to perform: " \
                            r"ec2:TerminateInstances on resource:.*"
    with pytest.raises(Exception, match=expected_error_string):
        access_manager.aws_api.ec2_client.dispose_instance_raw(request)


@pytest.mark.done
@pytest.mark.parametrize("aws_api_account", RuntimeData.aws_api_accounts)
def test_user_access_lambda(aws_api_account):
    """
    Test lambda_invocation

    :param aws_api_account:
    :return:
    """
    lambda_name = mock_values["credentials_test_invoke_lambda_name"]
    request = {"FunctionName": lambda_name,
               "InvocationType": "DryRun"
               }

    AWSAccount.set_aws_account(aws_api_account)
    AWSAccount.set_aws_region(Region.get_region("us-west-2"))
    expected_error_string = r"An error occurred \(AccessDeniedException\) when calling the Invoke operation: User: .* is not authorized to perform: lambda:InvokeFunction on resource:.*:function:" + \
                            lambda_name + " because no identity-based policy allows the lambda:InvokeFunction action"
    with pytest.raises(Exception, match=expected_error_string):
        access_manager.aws_api.lambda_client.invoke_raw(request)


@pytest.mark.wip
def test_cleanup_user_credentials():
    """
    Cleanup generated credentials.

    :return:
    """

    response = cleanup_user_credentials()
    assert response is not None
