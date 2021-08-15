"""
AWS clietn to handle service API requests.
"""
import pdb


from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.secrets_manager_secret import SecretsManagerSecret
from horey.h_logger import get_logger


logger = get_logger()


class SecretsManagerClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "secretsmanager"
        super().__init__(client_name)

    def get_secret(self, secret_name, region_name=None):
        if region_name is not None:
            AWSAccount.set_aws_region(region_name)

        raw_value = self.get_secret_value(secret_name)
        obj = SecretsManagerSecret(raw_value)

        return obj

    def put_secret(self, secret, region_name=None):
        if region_name is not None:
            AWSAccount.set_aws_region(region_name)

        if secret.secret_string is None:
            raise ValueError(secret.name)

        raw_value = self.raw_put_secret_string(secret.name, secret.secret_string)
        obj = SecretsManagerSecret(raw_value)

        return obj

    def get_all_secrets(self, full_information=True):
        """
        Get all lambda in all regions
        :param full_information:
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for response in self.execute(self.client.list_secrets, "SecretList"):
                obj = SecretsManagerSecret(response)
                final_result.append(obj)

                if full_information:
                    raw_value = self.get_secret_value(obj.name)
                    obj.update_value_from_raw_response(raw_value)

        return final_result

    def get_secret_value(self, secret_id):
        try:
            for response in self.execute(self.client.get_secret_value, None, raw_data=True,
                                     filters_req={"SecretId": secret_id}):
                return response
        except Exception:
            logger.error(f"Can not find secret {secret_id}")
            raise

    def raw_get_secret_string(self, secret_id, region=None):
        logger.info(f"Fetching secret value for secret '{secret_id}'")
        if region is not None:
            AWSAccount.set_aws_region(region)

        try:
            for response in self.execute(self.client.get_secret_value, None, raw_data=True,
                                     filters_req={"SecretId": secret_id}):
                return response["SecretString"]
        except Exception:
            logger.error(f"Can not find secret {secret_id}")
            raise

    def raw_create_secret_string(self, secret_id, value):
        try:
            for response in self.execute(self.client.create_secret, None, raw_data=True, filters_req={"Name": secret_id, "SecretString": value}):
                return response
        except Exception as exception_received:
            print(repr(exception_received))
            raise

    def raw_put_secret_string(self, secret_id, value, region=None):
        if region is not None:
            AWSAccount.set_aws_region(region)
        try:
            for response in self.execute(self.client.put_secret_value, None, raw_data=True, filters_req={"SecretId": secret_id, "SecretString": value}):
                return response
        except Exception as exception_received:
            if "ResourceNotFoundException" in repr(exception_received):
                return self.raw_create_secret_string(secret_id, value)
            raise
