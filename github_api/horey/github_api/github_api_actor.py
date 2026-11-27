"""
Github API entry point script.

"""

import argparse
from pathlib import Path

from horey.h_logger import get_logger

from horey.common_utils.actions_manager import ActionsManager
from horey.github_api.github_api import GithubAPI


logger = get_logger()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region get_workflow_dependency_tree
def get_workflow_dependency_tree_parser():
    description = "Get workflow dependency tree"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--workflow_file_path", required=True, type=str, help="workflow_file_path")
    parser.add_argument("--git_dir_path", required=False, type=str, help="git_dir_path")
    return parser


def get_workflow_dependency_tree(arguments) -> None:
    _api = GithubAPI()
    git_dir_path = Path(arguments.git_dir_path) if arguments.git_dir_path else None
    _, tree = _api.get_workflow_dependency_tree(Path(arguments.workflow_file_path), git_dir_path=git_dir_path)
    print(tree)

action_manager.register_action("get_workflow_dependency_tree", get_workflow_dependency_tree_parser, get_workflow_dependency_tree)
# endregion


if __name__ == "__main__":
    action_manager.call_action()
