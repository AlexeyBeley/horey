from horey.provision_constructor.system_function_unittest import SystemFunctionUnittest
from horey.common_utils.actions_manager import ActionsManager
import argparse
import pdb
import subprocess


class Check(SystemFunctionUnittest):
    def __init__(self):
        super().__init__()

    def check_swap_size(self, **kwargs):
        pdb.set_trace()
        ret = self.run_shell(["ls", "-l", "/dev/null"])

    def check_swappiness(self):
        pdb.set_trace()


action_manager = ActionsManager()


# region check_swappiness
def check_swappiness_parser():
    description = "check_swappiness"
    parser = argparse.ArgumentParser(description=description)
    parser.epilog = f"Usage: python3 {__file__} [options]"
    return parser


def check_swappiness(arguments) -> None:
    Check().check_swappiness()


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
    Check().check_swap_size(**arguments_dict)


action_manager.register_action("check_swap_size", check_swap_size_parser, check_swap_size)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

