"""
AWS client to handle service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.secrets_manager_secret import (
    SecretsManagerSecret,
)
from horey.h_logger import get_logger


logger = get_logger()


class SecretsManagerClient(Boto3Client):
    """
    Client to handle secrets aws service API calls.
    """

    def __init__(self):
        client_name = "secretsmanager"
        super().__init__(client_name)

    def get_secret(self, secret_name, region_name=None):
        """
        Standard.

        :param secret_name:
        :param region_name:
        :return:
        """

        if region_name is not None:
            AWSAccount.set_aws_region(region_name)

        raw_value = self.get_secret_value(secret_name)
        obj = SecretsManagerSecret(raw_value)

        return obj

    def put_secret(self, secret, region_name=None):
        """
        Standard.

        :param secret:
        :param region_name:
        :return:
        """

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

        final_result = []

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
        """
        Standard.

        :param secret_id:
        :return:
        """

        try:
            for response in self.execute(
                self.client.get_secret_value,
                None,
                raw_data=True,
                filters_req={"SecretId": secret_id},
            ):
                return response
        except Exception:
            logger.error(f"Can not find secret {secret_id}")
            raise

    def raw_get_secret_string(self, secret_id, region=None, ignore_missing=False):
        """
        Get secret.

        :param secret_id:
        :param region:
        :param ignore_missing:
        :return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)
        else:
            region = AWSAccount.get_aws_region()
        logger.info(f"Fetching secret value for secret '{secret_id}' region: {region.region_mark}")

        for response in self.execute(
            self.client.get_secret_value,
            None,
            raw_data=True,
            filters_req={"SecretId": secret_id},
            exception_ignore_callback=lambda exception_instance: "ResourceNotFoundException" in repr(exception_instance) and ignore_missing,
            instant_raise=True
        ):
            return response["SecretString"]

    def raw_create_secret_string(self, secret_id, value):
        """
        Create secret.

        :param secret_id:
        :param value:
        :return:
        """

        try:
            for response in self.execute(
                self.client.create_secret,
                None,
                raw_data=True,
                filters_req={"Name": secret_id, "SecretString": value},
            ):
                return response
        except Exception as exception_received:
            print(repr(exception_received))
            raise

    def raw_put_secret_string(self, secret_id, value, region=None):
        """
        Put or create a secret.

        :param secret_id:
        :param value:
        :param region:
        :return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)
        for response in self.execute(
            self.client.put_secret_value,
            None,
            raw_data=True,
            filters_req={"SecretId": secret_id, "SecretString": value},
            exception_ignore_callback=lambda exception_received: "ResourceNotFoundException" in repr(exception_received)
            ):
            return response

        return self.raw_create_secret_string(secret_id, value)

    def dispose_secret(self, name, region):
        """
        Delete the secret from region.

        :param name:
        :param region:
        :return:
        """

        request = {"SecretId": name}
        AWSAccount.set_aws_region(region)
        self.dispose_secret_raw(request)

    def dispose_secret_raw(self, request):
        """
        Standard.

        :param request:
        :return:
        """

        for response in self.execute(
            self.client.delete_secret,
            None,
            raw_data=True,
            filters_req=request,
            exception_ignore_callback=lambda exception_received: "ResourceNotFoundException" in repr(exception_received)
            ):
            return response

        return None
