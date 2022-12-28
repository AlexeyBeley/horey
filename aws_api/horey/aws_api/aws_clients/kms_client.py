"""
AWS lambda client to handle lambda service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.kms_key import KMSKey

logger = get_logger()


class KMSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "kms"
        super().__init__(client_name)

    def get_all_keys(self, region=None, full_information=True):
        """
        Get all keys in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_keys(region, full_information=full_information)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_keys(
                _region, full_information=full_information
            )

        return final_result

    def get_region_keys(self, region, full_information=True):
        """
        All keys in region.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.list_keys, "Keys"):
            obj = KMSKey(dict_src)

            if full_information:
                filters_req = {"KeyId": obj.id}

                for dict_response in self.execute(
                    self.client.describe_key, "KeyMetadata", filters_req=filters_req
                ):
                    obj.update_from_raw_response(dict_response)

                tags = list(
                    self.execute(
                        self.client.list_resource_tags,
                        "Tags",
                        filters_req=filters_req,
                        exception_ignore_callback=lambda error: "AccessDeniedException"
                        in repr(error),
                    )
                )

                obj.update_from_list_tags_response({"Tags": tags})

                aliases = list(
                    self.execute(
                        self.client.list_aliases,
                        "Aliases",
                        filters_req=filters_req,
                        exception_ignore_callback=lambda error: "AccessDeniedException"
                        in repr(error),
                    )
                )
                obj.update_from_list_aliases_response({"Aliases": aliases})

            final_result.append(obj)

        return final_result

    def get_key_by_tag(self, region, key_name, key_value):
        """
        Find specific key by tag.

        :param region:
        :param key_name:
        :param key_value:
        :return:
        """

        region_keys = self.get_region_keys(region)
        for region_key in region_keys:
            if (
                region_key.get_tag(
                    key_name,
                    ignore_missing_tag=True,
                    tag_key_specifier="TagKey",
                    tag_value_specifier="TagValue",
                )
                == key_value
            ):
                return region_key

        return None

    def provision_key(self, key):
        """
        Provision key and it's alias.

        :param key:
        :return:
        """

        region_key = self.get_key_by_tag(
            key.region,
            "name",
            key.get_tag(
                "name", tag_key_specifier="TagKey", tag_value_specifier="TagValue"
            ),
        )

        if region_key is None:
            AWSAccount.set_aws_region(key.region)
            response = self.provision_key_raw(key.generate_create_request())
            region_key = KMSKey({})
            region_key.update_from_raw_response(response)

        del_requests, create_requests = region_key.generate_alias_provision_requests(key)

        for del_request in del_requests:
            self.delete_alias_raw(del_request)

        for create_request in create_requests:
            self.create_alias_raw(create_request)

    def provision_key_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating key: {request_dict}")
        for response in self.execute(
            self.client.create_key, "KeyMetadata", filters_req=request_dict
        ):
            return response

    def delete_alias_raw(self, request_dict):
        """
        Delete the alias from a key.

        :param request_dict:
        :return:
        """
        logger.info(f"Deleting key alias: {request_dict}")
        for response in self.execute(
            self.client.delete_alias, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def create_alias_raw(self, request_dict):
        """
        Create and alias.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating key alias: {request_dict}")
        for response in self.execute(
            self.client.create_alias, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def create_key(self, name=None):
        """
                filters_req = dict()
        if name is not None:
            filters_req["Tags"] = ({"TagKey": "name", "TagValue": name},)
            filters_req["Description"] = name

        for response in self.execute(
            self.client.create_key, "KeyMetadata", filters_req=filters_req
        ):
            logger.info(
                f"Created KMS key name: {response['Description']} arn: {response['Arn']}"
            )

        filters_req = dict()
        filters_req["AliasName"] = f"alias/{name}"

        try:
            for _ in self.execute(
                self.client.delete_alias, "ResponseMetadata", filters_req=filters_req
            ):
                logger.info(f"Deleted {filters_req['AliasName']} from KMS key")
        except Exception as exception_received:
            repr_exception_received = repr(exception_received)
            if (
                "not" not in repr_exception_received
                or "found" not in repr_exception_received
            ):
                raise
            logger.info(repr_exception_received)

        filters_req["TargetKeyId"] = response["KeyId"]
        for _ in self.execute(
            self.client.create_alias, "ResponseMetadata", filters_req=filters_req
        ):
            logger.info(f"Created {filters_req['AliasName']} for KMS key")

        :param name:
        :return:
        """

        raise RuntimeError("Deprecated")
