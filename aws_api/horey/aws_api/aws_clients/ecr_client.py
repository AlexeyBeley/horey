"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from base64 import b64decode
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount


class ECRClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ecr"
        super().__init__(client_name)

    def get_authorization_info(self):
        current_account = AWSAccount.get_aws_account()

        lst_ret = list(self.execute(self.client.get_authorization_token, "authorizationData", filters_req={"registryIds": [current_account.id]}))
        for dict_src in lst_ret:
            auth_user_token = b64decode(dict_src['authorizationToken']).decode()
            user_name, decoded_token = auth_user_token.split(":")
            dict_src["user_name"] = user_name
            dict_src["decoded_token"] = decoded_token
            dict_src["proxy_host"] = dict_src["proxyEndpoint"][len("https://"):]
        return lst_ret

    def create_repository(self, repo_name):
        try:
            for _ in self.execute(self.client.create_repository, "repository", filters_req={"repositoryName": repo_name}):
                return True
        except Exception as e:
            e_lower_repr = repr(e).lower()
            if "repository" in e_lower_repr and "already" in e_lower_repr and "exists" in e_lower_repr:
                return True

        return False
