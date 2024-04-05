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
    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "NextMarker"

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
        logger.info(f"kms_client fetching KMS keys from region {region.region_mark}")
        for dict_src in self.execute(self.get_session_client(region=region).list_keys, "Keys"):
            obj = KMSKey(dict_src)

            if full_information:
                filters_req = {"KeyId": obj.id}

                logger.info(f"kms_client fetching more information about key {filters_req}")
                for dict_response in self.execute(
                        self.get_session_client(region=region).describe_key, "KeyMetadata", filters_req=filters_req,
                        exception_ignore_callback=
                        lambda error: "NotFoundException" in repr(error)
                ):
                    obj.update_from_raw_response(dict_response)

                tags = list(
                    self.execute(
                        self.get_session_client(region=region).list_resource_tags,
                        "Tags",
                        filters_req=filters_req,
                        exception_ignore_callback=lambda error: "AccessDeniedException"
                                                                in repr(error),
                    )
                )

                obj.update_from_list_tags_response({"Tags": tags})

                aliases = list(
                    self.execute(
                        self.get_session_client(region=region).list_aliases,
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
        found_keys = []
        for region_key in region_keys:
            if region_key.enabled is None:
                raise RuntimeError("Looks like AWS broke the API again. 'Enabled' was not set.")

            if not region_key.enabled:
                continue

            if (
                    region_key.get_tag(
                        key_name,
                        ignore_missing_tag=True,
                        tag_key_specifier="TagKey",
                        tag_value_specifier="TagValue",
                    )
                    == key_value
            ):
                found_keys.append(region_key)

        if len(found_keys) == 0:
            return None

        if len(found_keys) == 1:
            return found_keys[0]

        raise RuntimeError(f"Found more then 1 key with the same '{key_name}: {key_value}'."
                           f" Appears {len(found_keys)} times.")

    def provision_key(self, key: KMSKey):
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
            response = self.provision_key_raw(key.region, key.generate_create_request())
            region_key = KMSKey({})
            region_key.update_from_raw_response(response)
        else:
            request = region_key.generate_tag_resource_request(key)
            if request:
                self.tag_resource_raw(key.region, request)

        del_requests, create_requests = region_key.generate_alias_provision_requests(key)

        for del_request in del_requests:
            self.delete_alias_raw(key.region, del_request)

        for create_request in create_requests:
            self.create_alias_raw(region_key.region, create_request)

        key.id = region_key.id

    def tag_resource_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Tagging KMS key: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).tag_resource, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def deprecate_key(self, key: KMSKey, days=7):
        """
        Deprecate key - schedule key deletion to specified period.

        :param days:
        :param key:
        :return:
        """

        if key.id is None:
            raise NotImplementedError("Key must have 'id' set")

        response = self.schedule_key_deletion_raw(key.region, key.generate_schedule_key_deletion_request(days))
        return response

    def schedule_key_deletion_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Deleting key: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).schedule_key_deletion, None, raw_data=True,
                filters_req=request_dict
        ):
            return response

    def provision_key_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating key: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_key, "KeyMetadata", filters_req=request_dict
        ):
            return response

    def delete_alias_raw(self, region, request_dict):
        """
        Delete the alias from a key.

        :param request_dict:
        :return:
        """
        logger.info(f"Deleting key alias: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_alias, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def create_alias_raw(self, region, request_dict):
        """
        Create and alias.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating key alias: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_alias, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def create_key(self, name=None):
        """
                filters_req = dict()
        if name is not None:
            filters_req["Tags"] = ({"TagKey": "name", "TagValue": name},)
            filters_req["Description"] = name

        for response in self.execute(
            self.get_session_client(region=region).create_key, "KeyMetadata", filters_req=filters_req
        ):
            logger.info(
                f"Created KMS key name: {response['Description']} arn: {response['Arn']}"
            )

        filters_req = dict()
        filters_req["AliasName"] = f"alias/{name}"

        try:
            for _ in self.execute(
                self.get_session_client(region=region).delete_alias, "ResponseMetadata", filters_req=filters_req
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
            self.get_session_client(region=region).create_alias, "ResponseMetadata", filters_req=filters_req
        ):
            logger.info(f"Created {filters_req['AliasName']} for KMS key")

        :param name:
        :return:
        """

        raise RuntimeError("Deprecated")
