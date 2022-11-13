import argparse
import pdb


class ActionsManager:
    def __init__(self):
        self.actions = dict()

    def register_action(
        self, argparse_action_name, get_parser_function, action_function
    ):
        self.actions[argparse_action_name] = get_parser_function, action_function

    def call_action(self, pass_unknown_args=False):
        """
        parse_known_args - if Tr
        """
        description = "Action registration and calling"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            "--action",
            required=True,
            type=str,
            help=f"Action to perform- one of {list(self.actions.keys())}",
        )
        parser.epilog = f"Usage: python {__file__} --action ACTION_NAME"

        arguments, rest_args = parser.parse_known_args()

        if arguments.action not in self.actions:
            raise ValueError(
                f"Action '{arguments.action}' is not one of the registered: '{list(self.actions.keys())}'"
            )

        get_parser_function, action_function = self.actions[arguments.action]
        if not pass_unknown_args:
            return action_function(get_parser_function().parse_args(rest_args))

        arguments, rest_args = get_parser_function().parse_known_args(rest_args)
        parser = argparse.ArgumentParser()
        for argument in rest_args:
            if argument.startswith("--"):
                parser.add_argument(argument, type=str)
        configuration_args = parser.parse_args(rest_args)
        return action_function(arguments, vars(configuration_args))
