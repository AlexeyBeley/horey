"""
Github Action
"""

from horey.github_api.actions.base_object import BaseObject


class Action(BaseObject):
    """
    Github Action
    """

    def __init__(self):
        self.name = None
        super().__init__()

