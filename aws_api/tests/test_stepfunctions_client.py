"""
Test aws stepfunctions client.

"""
import json
import os

from horey.aws_api.aws_clients.stepfunctions_client import StepfunctionsClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.stepfunctions_state_machine import StepfunctionsStateMachine
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()

accounts_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "ignore",
        "aws_api_managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
definition_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "step_definition.json"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring


def test_init_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(StepfunctionsClient(), StepfunctionsClient)


def test_get_all_state_machines():
    client = StepfunctionsClient()
    objs = client.get_all_state_machines()
    assert objs is not None


def test_get_region_state_machines():
    client = StepfunctionsClient()
    objs = client.get_region_state_machines("eu-west-2")
    assert objs is not None


def test_provision_state_machine():
    client = StepfunctionsClient()
    state_machine = StepfunctionsStateMachine({})
    state_machine.region = Region.get_region("us-west-2")
    state_machine.name = "test_name_1"
    state_machine.role_arn = mock_values["state_machine_iam_role_arn"]
    state_machine.logging_configuration = {
      "level": "ALL",
      "includeExecutionData": True,
      "destinations": [
        {
          "cloudWatchLogsLogGroup": {
            "logGroupArn": mock_values["state_machine_log_group_arn"]
          }
        }
      ]
    }
    state_machine.tags = [{"Key": "Name", "Value": state_machine.name}]
    with open(definition_file_path, encoding="utf-8") as fh:
        definition = json.dumps(json.load(fh))
    state_machine.definition = definition
    client.provision_state_machine(state_machine)
    assert state_machine.arn is not None


if __name__ == "__main__":
    # test_init_client()
    # test_get_all_state_machines()
    # test_get_region_state_machines()
    test_provision_state_machine()
