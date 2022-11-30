"""
API to manage human beings.
"""


class HumanAPI:
    """
    Manage work/work balance
    """

    def __init__(self):
        self._sprint = None

    @property
    def sprint(self):
        if self._sprint is None:
            load_sprints
        return self._sprint

