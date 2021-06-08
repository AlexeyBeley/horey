"""
AWS client to handle service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
import pdb


class EventBridgeClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    NEXT_PAGE_REQUEST_KEY = "NextToken"
    NEXT_PAGE_RESPONSE_KEY = "NextToken"
    NEXT_PAGE_INITIAL_KEY = ""

    def __init__(self):
        client_name = "cloudfront"
        super().__init__(client_name)

    def get_all_rules(self, full_information=True):
        """
        Get all lambda in all regions
        :param full_information:
        :return:
        """
        final_result = list()
        for response in self.execute(self.client.list_rules, "Rules"):
            pdb.set_trace()
            for item in response["Items"]:
                obj = CloudfrontDistribution(item)
                final_result.append(obj)

            if full_information:
                pass

        return final_result
