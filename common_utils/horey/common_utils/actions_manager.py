import argparse


class ActionsManager:
    def __init__(self):
        self.actions = dict()

    def register_action(self, argparse_action_name, get_parser_function, action_function):
        self.actions[argparse_action_name] = get_parser_function, action_function

    def call_action(self):
        description = "Action registration and calling"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--action", required=True, type=str, help=f"Action to perform- one of {list(self.actions.keys())}")
        parser.epilog = f"Usage: python {__file__} --action ACTION_NAME"

        arguments, rest_args = parser.parse_known_args()

        if arguments.action not in self.actions:
            raise ValueError(f"Action '{arguments.action}' is not one of the registered: '{list(self.actions.keys())}'")

        get_parser_function, action_function = self.actions[arguments.action]
        action_function(get_parser_function().parse_args(rest_args))

    def call_action_with_configuration(self):
        description = "Action registration and calling"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--action", required=True, type=str, help=f"Action to perform- one of {list(self.actions.keys())}")
        parser.epilog = f"Usage: python {__file__} --action ACTION_NAME"

        arguments, rest_args = parser.parse_known_args()

        if arguments.action not in self.actions:
            raise ValueError(f"Action '{arguments.action}' is not one of the registered: '{list(self.actions.keys())}'")

        get_parser_function, action_function = self.actions[arguments.action]
        action_function(get_parser_function().parse_args(rest_args))