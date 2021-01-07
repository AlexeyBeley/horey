"""
AWS lambda client to handle lambda service API requests.
"""
from boto3_client import Boto3Client
from aws_lambda import AWSLambda
from aws_account import AWSAccount


class LambdaClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "NextMarker"
    NEXT_PAGE_INITIAL_KEY = ""

    def __init__(self):
        client_name = "lambda"
        super().__init__(client_name)

    def get_all_lambdas(self, full_information=True):
        """
        Get all lambda in all regions
        :param full_information:
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for response in self.execute(self.client.list_functions, "Functions"):
                obj = AWSLambda(response)
                final_result.append(obj)

                if full_information:
                    pass
        return final_result
