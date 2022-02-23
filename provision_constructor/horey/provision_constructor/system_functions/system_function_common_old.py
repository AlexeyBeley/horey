from horey.common_utils.actions_manager import ActionsManager
import argparse
import pdb


class SystemFunctionCommon:
    def __init__(self):
        super().__init__()

    @staticmethod
    def add_line_to_file(line=None, file_path=None):
        if not line.endswith("\n"):
            line = line + "\n"

        with open(file_path, "r") as file_handler:
            lines = file_handler.readlines()
            if line in lines:
                return

        with open(file_path, "a") as file_handler:
            file_handler.write(line)

def add_line_to_file_parser():
    description = "add_line_to_file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--line", required=True, type=str, help="Line to be added")
    parser.add_argument("--file_path", required=True, type=str, help="Path to the file")

    parser.epilog = f"Usage: python3 {__file__} [options]"
    return parser


def add_line_to_file(arguments) -> None:
    arguments_dict = vars(arguments)
    SystemFunctionCommon.add_line_to_file(**arguments_dict)

action_manager = ActionsManager()


# region add_line_to_file



action_manager.register_action("add_line_to_file", add_line_to_file_parser, add_line_to_file)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

