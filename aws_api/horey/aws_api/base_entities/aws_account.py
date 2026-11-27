"""
AWS account management module - defines how to connect to an account in order to run API calls in in.
"""
from enum import Enum
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

logger = get_logger()


class AWSAccount:
    """
    Class defining account metadata and the connection steps to perform in order to manage the account.
    """

    _CURRENT_ACCOUNT = None
    _CURRENT_REGION = None
    KNOWN_IDS = []

    def __init__(self):
        self._id = None
        self.name = None
        self.regions = {}
        self.connection_steps = []
        self._default_region = None

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

        logger.info(f"Setting AWS account to {value}")
        AWSAccount._CURRENT_ACCOUNT = value

    @staticmethod
    def get_default_region():
        """
        Get current region to work against.
        :return:
        """
        return AWSAccount._CURRENT_REGION

    @staticmethod
    def get_account_default_region():
        """
        Get current region to work against.
        :return:
        """

        return list(AWSAccount.get_aws_account().regions.values())[0]

    @staticmethod
    def get_aws_region():
        """
        Get current region to work against.
        :return:
        """
        raise RuntimeError("""Use get_default_region instead
        logger.error("Use get_default_region instead")
        return AWSAccount.get_default_region()""")

    @staticmethod
    def set_aws_default_region(value):
        """
        Set current region to work against.
        :return:
        """

        logger.info(f"Setting AWS default region to {value}")
        if (AWSAccount._CURRENT_REGION is not None) and (AWSAccount._CURRENT_REGION != value):
            raise ValueError(f"Default region can not be reset {str(AWSAccount._CURRENT_REGION)=}, {str(value)}")

        if isinstance(value, str):
            value = Region.get_region(value)

        if not isinstance(value, Region):
            raise ValueError(f"{value} is not of type Region")

        AWSAccount._CURRENT_REGION = value

    @staticmethod
    def set_aws_region(value):
        """
        Set current region to work against.
        :return:
        """

        logger.error("Use set_aws_default_region instead")
        return AWSAccount.set_aws_default_region(value)

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

    @property
    def default_region(self):
        """
        Get unique identifier of the account.
        :return:
        """

        if self._default_region is None:
            if self.regions:
                self._default_region = list(self.regions.values())[0]
            elif self.connection_steps:
                self._default_region = self.connection_steps[0].region

        return self._default_region

    @default_region.setter
    def default_region(self, value):
        """
        Standard

        :param value:
        :return:
        """

        self._default_region = value

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

    def add_region(self, region):
        """
        Add region to managed regions.

        :param region:
        :return:
        """

        if region.region_mark in self.regions:
            return

        self.regions[region.region_mark] = region

    def get_regions(self):
        """
        Get managed regions.

        :return:
        """
        return self.regions.values()

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
            CURRENT_ROLE = 3

        def __init__(self, dict_src):
            self.aws_access_key_id = None
            self.aws_secret_access_key = None
            self.profile_name = None
            self.role_arn = None
            self.region = None
            self.type = None
            self.external_id = None

            if "region_mark" in dict_src:
                self.region = Region.get_region(dict_src["region_mark"])

            if "profile" in dict_src:
                logger.info(
                    f"Setting connection step type to AWSAccount.ConnectionStep.Type.PROFILE: {dict_src}"
                )
                self.type = AWSAccount.ConnectionStep.Type.PROFILE
                self.profile_name = dict_src["profile"]
            elif "assume_role" in dict_src:
                self.type = AWSAccount.ConnectionStep.Type.ASSUME_ROLE
                self.role_arn = dict_src["assume_role"]
            elif "role" in dict_src:
                if dict_src["role"] != "current":
                    raise ValueError(dict_src["role"])
                logger.info(
                    f"Setting connection step type to AWSAccount.ConnectionStep.Type.CURRENT_ROLE: {dict_src}"
                )
                self.type = AWSAccount.ConnectionStep.Type.CURRENT_ROLE
            elif "aws_access_key_id" in dict_src and "aws_secret_access_key" in dict_src:
                self.type = AWSAccount.ConnectionStep.Type.CREDENTIALS
                self.aws_access_key_id = dict_src["aws_access_key_id"]
                self.aws_secret_access_key = dict_src["aws_secret_access_key"]
            else:
                raise NotImplementedError(f"Unknown {dict_src}")

            if "external_id" in dict_src:
                self.external_id = dict_src["external_id"]
