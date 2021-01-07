"""
AWS account management module - defines how to connect to an account in order to run API calls in in.
"""
from enum import Enum
from region import Region


class AWSAccount:
    """
    Class defining account metadata and the connection steps to perform in order to manage the account.
    """
    _CURRENT_ACCOUNT = None
    _CURRENT_REGION = None
    KNOWN_IDS = []

    @staticmethod
    def get_aws_account():
        """
        Get current account to work against.
        :return:
        """
        return AWSAccount._CURRENT_ACCOUNT

    @staticmethod
    def set_aws_account(value):
        """
        Set current account to work against.
        :param value:
        :return:
        """
        AWSAccount._CURRENT_ACCOUNT = value

    @staticmethod
    def get_aws_region():
        """
        Get current region to work against.
        :return:
        """
        return AWSAccount._CURRENT_REGION

    @staticmethod
    def set_aws_region(value):
        """
        Set current region to work against.
        :return:
        """
        if not isinstance(value, Region):
            raise ValueError(f"{value} is not of type Region")
        AWSAccount._CURRENT_REGION = value

    def __init__(self):
        self._id = None
        self.name = None
        self.regions = dict()
        self.connection_steps = []

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def id(self):
        """
        Get unique identifier of the account.
        :return:
        """
        if self._id is None:
            raise RuntimeError("Accessing unset attribute ID")
        return self._id

    @id.setter
    def id(self, value):
        """
        Set unique identifier of the account.
        :return:
        """
        if not isinstance(value, str):
            raise ValueError(f"ID must be string: {value}")

        if self._id is not None:
            raise ValueError(f"Trying to reset id: {self._id} with value: {value}")

        self._id = value

    def init_from_dict(self, dict_src):
        """
        Example:

        :param dict_src:
        :return:
        """
        raise NotImplementedError("Broke after refactoring")

    def _init_connection_steps_from_list(self, lst_src):
        """
        Init connection steps

        :param lst_src:
        :return:
        """
        for connection_step_dict in lst_src:
            connection_step = AWSAccount.ConnectionStep(connection_step_dict)
            self.connection_steps.append(connection_step)

    class ConnectionStep:
        """
        Single step to perform in a chain of steps to connect
        """
        class Type(Enum):
            """
            Connection step types
            """
            CREDENTIALS = 0
            PROFILE = 1
            ASSUME_ROLE = 2

        def __init__(self, dict_src):
            self.aws_access_key_id = None
            self.aws_secret_access_key = None
            self.profile_name = None
            self.role_arn = None
            self.region = None
            self.type = None
            self.external_id = None

            if "region_mark" in dict_src:
                self.region = Region()
                self.region.region_mark = dict_src["region_mark"]

            if "credentials" in dict_src:
                raise NotImplementedError()

            if "profile" in dict_src:
                self.type = AWSAccount.ConnectionStep.Type.PROFILE
                self.profile_name = dict_src["profile"]
            elif "assume_role" in dict_src:
                self.type = AWSAccount.ConnectionStep.Type.ASSUME_ROLE
                self.role_arn = dict_src["assume_role"]
            else:
                raise NotImplementedError(f"Unknown {dict_src}")

            if "external_id" in dict_src:
                self.external_id = dict_src["external_id"]
