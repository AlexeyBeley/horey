"""
Kubernetes account management module - defines how to connect to an account in order to run API calls in in.

"""


class KubernetesAccount:
    """
    Class defining account metadata and the connection steps to perform in order to manage the account.
    """

    _CURRENT_ACCOUNT = None

    @staticmethod
    def get_kubernetes_account():
        """
        Get current account to work against.
        :return:
        """
        return KubernetesAccount._CURRENT_ACCOUNT

    @staticmethod
    def set_kubernetes_account(value):
        """
        Set current account to work against.
        :param value:
        :return:
        """
        KubernetesAccount._CURRENT_ACCOUNT = value

    def __init__(self, endpoint=None, token=None, cadata=None):
        self.endpoint = endpoint
        self.token = token
        self.cadata = cadata
