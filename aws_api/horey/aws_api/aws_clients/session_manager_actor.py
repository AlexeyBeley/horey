# pylint: skip-file
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
    parser.add_argument(
        "--profile_name",
        required=True,
        type=str,
        help="profile name in .aws/credentials",
    )

    return parser


def set_session_credentials(arguments, configs_dict) -> None:
    configuration = AWSAPIConfigurationPolicy()
    configuration.configuration_file_full_path = "~/Desktop/tmp/configuration_values.py"
    configuration.init_from_file()

    accounts = CommonUtils.load_object_from_module(configuration.accounts_file, "main")
    AWSAccount.set_aws_account(accounts[configuration.aws_api_account])

    session = SessionsManager.connect_session()
    credentials = session.get_credentials()
    credentials = credentials.get_frozen_credentials()

    ret = f"\n\n[{arguments.profile_name}]"
    ret += f"\naws_access_key_id = {credentials.access_key}"
    ret += f"\naws_secret_access_key = {credentials.secret_key}"
    ret += f"\naws_session_token = {credentials.token}"

    with open("~/.aws/credentials") as file_handler:
        contents = file_handler.read()

    if arguments.profile_name in contents:
        start_index = contents.index(f"[{arguments.profile_name}]")

        try:
            end_index = contents.index("[", start_index + 1)
            tail_string = "\n\n" + contents[end_index:].strip("\n")
        except ValueError:
            tail_string = ""

        new_contents = contents[:start_index].strip("\n") + ret + tail_string
        with open("~/.aws/credentials", "w+") as file_handler:
            file_handler.write(new_contents)

    else:
        with open("~/.aws/credentials", "a+") as file_handler:
            file_handler.write(ret)


action_manager.register_action(
    "set_session_credentials", set_session_credentials_parser, set_session_credentials
)
# endregion


if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)
