"""
GCP account management module - defines how to connect to an account in order to run API calls in in.
"""
import pdb
from enum import Enum
from horey.gcp_api.base_entities.region import Region


class GCPAccount:
    """
    Class defining account metadata and the connection steps to perform in order to manage the account.
    """

    _CURRENT_ACCOUNT = None
    _CURRENT_REGION = None
    KNOWN_IDS = []

    @staticmethod
    def get_gcp_account():
        """
        Get current account to work against.
        :return:
        """
        return GCPAccount._CURRENT_ACCOUNT

    @staticmethod
    def set_gcp_account(value):
        """
        Set current account to work against.
        :param value:
        :return:
        """
        GCPAccount._CURRENT_ACCOUNT = value

    @staticmethod
    def get_gcp_region():
        """
        Get current region to work against.
        :return:
        """
        return GCPAccount._CURRENT_REGION

    @staticmethod
    def set_gcp_region(value):
        """
        Set current region to work against.
        :return:
        """
        if not isinstance(value, Region):
            raise ValueError(f"{value} is not of type Region")
        GCPAccount._CURRENT_REGION = value

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
            connection_step = GCPAccount.ConnectionStep(connection_step_dict)
            self.connection_steps.append(connection_step)

    class ConnectionStep:
        """
        Single step to perform in a chain of steps to connect
        """

        class Type(Enum):
            """
            Connection step types
            """

        def __init__(self, dict_src):
            self.project_name = None
            self.project = None
            self.client_id = None
            self.secret = None

            for key, value in dict_src.items():
                setattr(self, key, value)
