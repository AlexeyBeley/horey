from horey.deployer.system_function_unittest import SystemFunctionUnittest
from argparse import ArgumentParser
from horey.common_utils.actions_manager import ActionsManager
import argparse


class Check(SystemFunctionUnittest):
    def __init__(self, argv):
        super().__init__()


action_manager = ActionsManager()


# region check_swappiness
def check_swappiness_parser():
    description = "check_swappiness"
    parser = argparse.ArgumentParser(description=description)
    parser.epilog = f"Usage: python3 {__file__} [options]"
    return parser


def check_swappiness(arguments) -> None:
    arguments_dict = vars(arguments)
    for key in list(arguments_dict.keys()):
        arguments_value = arguments_dict.get(key)
        if arguments_value is None or \
                isinstance(arguments_value, str) and arguments_value.lower() == "none":
            del arguments_dict[key]
        elif isinstance(arguments_value, str) and arguments_value.lower() in ["true", "false"]:
            arguments_dict[key] = True if arguments_value.lower() == "true" else False

    Check(arguments_dict).check_swappiness()


action_manager.register_action("check_swappiness", check_swappiness_parser, check_swappiness)
# endregion


# region check_swap_size
def check_swap_size_parser():
    description = "check_swap_size"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--swap_size", required=True, type=str, help=f"GB swap_size")

    parser.epilog = f"Usage: python3 {__file__} [options]"
    return parser


def check_swap_size(arguments) -> None:
    arguments_dict = vars(arguments)
    for key in list(arguments_dict.keys()):
        arguments_value = arguments_dict.get(key)
        if arguments_value is None or \
                isinstance(arguments_value, str) and arguments_value.lower() == "none":
            del arguments_dict[key]
        elif isinstance(arguments_value, str) and arguments_value.lower() in ["true", "false"]:
            arguments_dict[key] = True if arguments_value.lower() == "true" else False

    Check(arguments_dict).check_swap_size()


action_manager.register_action("check_swap_size", check_swap_size_parser, check_swap_size)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

