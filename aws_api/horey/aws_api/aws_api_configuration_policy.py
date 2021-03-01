from horey.configuration_policy import ConfigurationPolicy


class AWSAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._aws_api_regions = None
        self._aws_api_account = None

    @property
    def aws_api_regions(self):
        if self._aws_api_regions is None:
            raise ValueError("aws_api_regions were not set")
        return self._aws_api_regions

    @aws_api_regions.setter
    def aws_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(f"aws_api_regions must be a list received {value} of type: {type(value)}")

        self._aws_api_regions = value

    @property
    def aws_api_account(self):
        if self._aws_api_account is None:
            raise ValueError("aws_api_account were not set")
        return self._aws_api_account

    @aws_api_account.setter
    def aws_api_account(self, value):
        if not isinstance(value, str):
            raise ValueError(f"aws_api_account must be a string received {value} of type: {type(value)}")

        self._aws_api_account = value
