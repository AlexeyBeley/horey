"""
AWS lambda client to handle lambda service API requests.
"""
import pdb

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import LambdaEventSourceMapping

from horey.aws_api.base_entities.aws_account import AWSAccount

from horey.h_logger import get_logger

logger = get_logger()


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

    def get_all_lambdas(self, full_information=True, region=None):
        """
        Get all lambda in all regions
        :param full_information:
        :return:
        """
        if region is not None:
            return self.get_region_lambdas(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_lambdas(region)

        return final_result

    def get_region_lambdas(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.list_functions, "Functions"):
            obj = AWSLambda(response)
            final_result.append(obj)
        return final_result

    def get_all_event_source_mappings(self, full_information=True, region=None):
        """
        Get all event_source_mapping in all regions
        :param full_information:
        :return:
        """

        if region is not None:
            return self.get_region_event_source_mappings(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_event_source_mappings(region)

        return final_result

    def get_region_event_source_mappings(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for response in self.execute(self.client.list_event_source_mappings, "EventSourceMappings"):
            obj = LambdaEventSourceMapping(response)
            final_result.append(obj)
        return final_result

    def provision_lambda(self, aws_lambda: AWSLambda, force=False):
        region_lambdas = self.get_region_lambdas(aws_lambda.region)
        for region_lambda in region_lambdas:
            if region_lambda.name == aws_lambda.name:
                aws_lambda.update_from_raw_response(region_lambda.dict_src)
                if force:
                    response = self.update_function_code_raw(aws_lambda.generate_update_function_code_request())
                    del response["ResponseMetadata"]
                    aws_lambda.update_from_raw_response(response)
                return

        AWSAccount.set_aws_region(aws_lambda.region)
        response = self.provision_lambda_raw(aws_lambda.generate_create_request())

        aws_lambda.update_from_raw_response(response)

    def provision_lambda_raw(self, request_dict):
        logger.info(f"Creating lambda: {request_dict}")
        for response in self.execute(self.client.create_function, None, raw_data=True,
                                     filters_req=request_dict):
            pdb.set_trace()
            return response

    def update_function_code_raw(self, request_dict):
        logger.info(f"Updating lambda code lambda: {request_dict}")
        for response in self.execute(self.client.update_function_code, None, raw_data=True,
                                     filters_req=request_dict):
            return response
