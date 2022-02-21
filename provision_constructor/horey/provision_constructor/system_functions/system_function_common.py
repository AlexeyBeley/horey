from horey.common_utils.actions_manager import ActionsManager
import argparse
import pdb


class SystemFunctionCommon:
    def __init__(self):
        super().__init__()

    def add_line_to_file(self, line=None, file_path=None):
        """
        #collect
        #swapon --show

        #output
        #NAME       TYPE   SIZE USED PRIO
        #/swapfile  file 1024M   0B   -2
        @param kwargs:
        @return:
        """
        pdb.set_trace()


action_manager = ActionsManager()


# region add_line_to_file
def add_line_to_file_parser():
    description = "add_line_to_file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--line", required=True, type=str, help="Line to be added")
    parser.add_argument("--file_path", required=True, type=str, help="Path to the file")

    parser.epilog = f"Usage: python3 {__file__} [options]"
    return parser


def add_line_to_file(arguments) -> None:
    arguments_dict = vars(arguments)
    SystemFunctionCommon().add_line_to_file(**arguments_dict)


action_manager.register_action("add_line_to_file", add_line_to_file_parser, add_line_to_file)
# endregion

if __name__ == "__main__":
    action_manager.call_action()

