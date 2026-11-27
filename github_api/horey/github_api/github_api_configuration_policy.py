from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class GithubAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        self._owner = None
        self._group_id = None
        self._pat = None

        super().__init__()

    @property
    def owner(self):
        if self._owner is None:
            raise ValueError("owner was not set")
        return self._owner

    @owner.setter
    def owner(self, value):
        """
        http://127.0.0.1:3000
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"owner must be string received {value} of type: {type(value)}"
            )

        self._owner = value

    @property
    def group_id(self):
        if self._group_id is None:
            raise ValueError("group_id was not set")
        return self._group_id

    @group_id.setter
    def group_id(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"group_id must be string received {value} of type: {type(value)}"
            )

        self._group_id = value

    @property
    def pat(self):
        return self._pat

    @pat.setter
    def pat(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError(
                f"pat must be string or None received {value} of type: {type(value)}"
            )

        self._pat = value
