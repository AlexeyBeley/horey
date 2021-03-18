import pdb
import argparse

from horey.aws_api.aws_clients.sessions_manager import SessionsManager
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.common_utils.actions_manager import ActionsManager
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.base_entities.aws_account import AWSAccount


action_manager = ActionsManager()


# region run_job
def set_session_credentials_parser():
    # export AWS_PROFILE=user1d
    description = "Get session credentials"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--profile_name", required=True, type=str, help="profile name in .aws/credentials")

    return parser


def set_session_credentials(arguments, configs_dict) -> None:
    configuration = AWSAPIConfigurationPolicy()
    configuration.configuration_file_full_path = "/Users/alexeybe/Desktop/tmp/configuration_values.py"
    configuration.init_from_file()

    accounts = CommonUtils.load_object_from_module(configuration.accounts_file, "main")
    AWSAccount.set_aws_account(accounts[configuration.aws_api_account])

    session = SessionsManager.connect_session()
    credentials = session.get_credentials()
    credentials = credentials.get_frozen_credentials()

    ret = f"[{arguments.profile_name}]"
    ret += f"\n{credentials.token}"
    ret += f"\n{credentials.access_key}"
    ret += f"\n{credentials.secret_key}"

    with open("/Users/alexeybe/.aws/credentials") as file_handler:
        contents = file_handler.read()
    pdb.set_trace()

action_manager.register_action("set_session_credentials", set_session_credentials_parser, set_session_credentials)
# endregion


if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)
