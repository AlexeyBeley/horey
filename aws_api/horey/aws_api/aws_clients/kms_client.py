"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from boto3_client import Boto3Client
from h_logger import get_logger

logger = get_logger()


class KMSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "kms"
        super().__init__(client_name)

    def create_key(self, name=None):
        filters_req = dict()
        if name is not None:
            filters_req["Tags"] = ({"TagKey": "name", "TagValue": name},)
            filters_req["Description"] = name

        for response in self.execute(self.client.create_key, "KeyMetadata", filters_req=filters_req):
            logger.info(f"Created KMS key name: {response['Description']} arn: {response['Arn']}")

        filters_req = dict()
        filters_req["AliasName"] = f"alias/{name}"

        try:
            for _ in self.execute(self.client.delete_alias, "ResponseMetadata", filters_req=filters_req):
                logger.info(f"Deleted {filters_req['AliasName']} from KMS key")
        except Exception as exception_received:
            repr_exception_received = repr(exception_received)
            if "not" not in repr_exception_received or "found" not in repr_exception_received:
                raise
            logger.info(repr_exception_received)

        filters_req["TargetKeyId"] = response["KeyId"]
        for _ in self.execute(self.client.create_alias, "ResponseMetadata", filters_req=filters_req):
            logger.info(f"Created {filters_req['AliasName']} for KMS key")


