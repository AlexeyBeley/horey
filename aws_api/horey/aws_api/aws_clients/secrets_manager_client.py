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

    def get_secret(self, region, secret_name):
        """
        Standard.

        :param secret_name:
        :param region_name:
        :return:
        """

        raw_value = self.get_secret_value(region, secret_name)
        obj = SecretsManagerSecret(raw_value)

        return obj

    def put_secret(self, secret):
        """
        Standard.

        :param secret:
        :return:
        """

        if secret.secret_string is None:
            raise ValueError(secret.name)

        raw_value = self.raw_put_secret_string(secret.region, secret.name, secret.secret_string)
        obj = SecretsManagerSecret(raw_value)

        return obj

    def get_all_secrets(self, region=None, full_information=True):
        """
        Get all lambda in all regions

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        regions = [region] if region is not None else AWSAccount.get_aws_account().regions.values()
        for _region in regions:
            for response in self.execute(self.get_session_client(region=_region).list_secrets, "SecretList"):
                obj = SecretsManagerSecret(response)
                final_result.append(obj)

                if full_information:
                    raw_value = self.get_secret_value(_region, obj.name)
                    obj.update_value_from_raw_response(raw_value)

        return final_result

    def yield_secrets_raw(self, region, request=None):
        """
        Standard.

        :param request:
        :return:
        """

        yield from self.execute(self.get_session_client(region=region).list_secrets, "SecretList",
                                     filters_req=request)

    def get_secret_value(self, region, secret_id):
        """
        Standard.

        :param secret_id:
        :return:
        """

        try:
            for response in self.execute(
                    self.get_session_client(region=region).get_secret_value,
                    None,
                    raw_data=True,
                    filters_req={"SecretId": secret_id},
            ):
                return response
        except Exception:
            logger.error(f"Can not find secret {secret_id}")
            raise

    def raw_get_secret_string(self, region, secret_id, ignore_missing=False):
        """
        Get secret.

        :param secret_id:
        :param region:
        :param ignore_missing:
        :return:
        """

        logger.info(f"Fetching secret value for secret '{secret_id}' region: {region}")

        for response in self.execute(
                self.get_session_client(region=region).get_secret_value,
                None,
                raw_data=True,
                filters_req={"SecretId": secret_id},
                exception_ignore_callback=lambda exception_instance: "ResourceNotFoundException" in repr(
                    exception_instance) and ignore_missing,
                instant_raise=True
        ):
            return response["SecretString"]

    def raw_create_secret_string(self, region, secret_id, value):
        """
        Create secret.

        :param secret_id:
        :param value:
        :return:
        """

        try:
            for response in self.execute(
                    self.get_session_client(region=region).create_secret,
                    None,
                    raw_data=True,
                    filters_req={"Name": secret_id, "SecretString": value},
            ):
                return response
        except Exception as exception_received:
            print(repr(exception_received))
            raise

    def raw_put_secret_string(self, region, secret_id, value):
        """
        Put or create a secret.

        :param secret_id:
        :param value:
        :param region:
        :return:
        """

        for response in self.execute(
                self.get_session_client(region=region).put_secret_value,
                None,
                raw_data=True,
                filters_req={"SecretId": secret_id, "SecretString": value},
                exception_ignore_callback=lambda exception_received: "ResourceNotFoundException" in repr(
                    exception_received)
        ):
            return response

        return self.raw_create_secret_string(region, secret_id, value)

    def dispose_secret(self, name, region):
        """
        Delete the secret from region.

        :param name:
        :param region:
        :return:
        """

        request = {"SecretId": name}
        self.dispose_secret_raw(region, request)

    def dispose_secret_raw(self, region, request):
        """
        Standard.

        :param request:
        :return:
        """

        for response in self.execute(
                self.get_session_client(region=region).delete_secret,
                None,
                raw_data=True,
                filters_req=request,
                exception_ignore_callback=lambda exception_received: "ResourceNotFoundException" in repr(
                    exception_received)
        ):
            return response

        return None
