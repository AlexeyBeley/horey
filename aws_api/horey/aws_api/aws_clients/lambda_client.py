"""
AWS lambda client to handle lambda service API requests.

Runtime example:
https://docs.aws.amazon.com/lambda/latest/dg/runtimes-walkthrough.html

"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import (
    LambdaEventSourceMapping,
)

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

    # pylint: disable= too-many-arguments
    def yield_lambdas(self, region=None, update_info=False, filters_req=None, full_information=True):
        """
        Yield lambdas

        :return:
        """

        regional_fetcher_generator = self.yield_lambdas_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  AWSLambda,
                                                  update_info=update_info,
                                                  full_information_callback=self.update_lambda_full_information if full_information else None,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_lambdas_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.list_functions, "Functions", filters_req=filters_req
        ):
            yield dict_src

    def get_all_lambdas(self, full_information=True, region=None):
        """
        Get all lambda in all regions
        :return:
        @param full_information:
        @param region:
        """

        return list(self.yield_lambdas(full_information=full_information, region=region))

    def get_region_lambdas(self, region, full_information=True):
        """
        Standard

        @param region:
        @param full_information:
        @return:
        """

        return list(self.yield_lambdas(full_information=full_information, region=region))

    def update_lambda_full_information(self, obj: AWSLambda):
        """
        Standard

        @param obj:
        @return:
        """

        logger.info(f"Fetching Lambda's '{obj.name}' policy if exists.")

        for response in self.execute(
            self.client.get_policy,
            None,
            raw_data=True,
            filters_req={"FunctionName": obj.name},
            exception_ignore_callback=lambda x: "ResourceNotFoundException" in repr(x),
        ):
            del response["ResponseMetadata"]
            obj.update_policy_from_get_policy_raw_response(response)

        for response in self.execute(
            self.client.get_function_concurrency,
            None,
            raw_data=True,
            filters_req={"FunctionName": obj.name}
        ):
            obj.reserved_concurrent_executions = response.get("ReservedConcurrentExecutions")

    def get_all_event_source_mappings(self, region=None):
        """
        Get all event_source_mapping in all regions
        :return:
        """

        if region is not None:
            return self.get_region_event_source_mappings(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_event_source_mappings(_region)

        return final_result

    def get_region_event_source_mappings(self, region):
        """
        Standard

        @param region:
        @return:
        """
        final_result = []
        AWSAccount.set_aws_region(region)
        for response in self.execute(
            self.client.list_event_source_mappings, "EventSourceMappings"
        ):
            obj = LambdaEventSourceMapping(response)
            final_result.append(obj)
        return final_result

    def update_lambda_information(self, aws_lambda, full_information=True):
        """
        Update lambda info if exists.

        @param aws_lambda:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(aws_lambda.region)
        for response in self.execute(
            self.client.get_function,
            None,
            raw_data=True,
            filters_req={"FunctionName": aws_lambda.name},
            exception_ignore_callback=lambda x: "ResourceNotFoundException" in repr(x),
        ):
            del response["ResponseMetadata"]
            aws_lambda.update_from_raw_get_function_response(response)
            break
        else:
            return False

        if full_information:
            self.update_lambda_full_information(aws_lambda)

        return True

    def provision_lambda(self, desired_aws_lambda: AWSLambda, force=None, update_code=False):
        """
        Add or update the Lambda configuration and Lambda code.

        @param desired_aws_lambda:
        @param force: deprecated
        @param update_code: Update the lambda code or update the configuration only.
        @return:
        """
        if force is not None:
            logger.warning("Deprecation: 'force' is going to be deprecated use update_code instead")
            update_code = force

        AWSAccount.set_aws_region(desired_aws_lambda.region)

        current_lambda = AWSLambda({})
        current_lambda.name = desired_aws_lambda.name
        current_lambda.region = desired_aws_lambda.region
        self.update_lambda_information(current_lambda, full_information=True)

        if current_lambda.arn is None:
            self.provision_lambda_raw(desired_aws_lambda.generate_create_request())
            if desired_aws_lambda.policy is not None:
                for (
                    add_permission_request
                ) in desired_aws_lambda.generate_add_permissions_requests():
                    self.add_permission_raw(add_permission_request)
                    self.wait_for_status(
                        current_lambda,
                        self.update_lambda_information,
                        [current_lambda.Status.SUCCESSFUL],
                        [current_lambda.Status.INPROGRESS],
                        [current_lambda.Status.FAILED],
                    )

        update_function_configuration_request = (
            current_lambda.generate_update_function_configuration_request(
                desired_aws_lambda
            )
        )
        if update_function_configuration_request is not None:
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )
            self.update_function_configuration_raw(
                update_function_configuration_request
            )
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )

        # concurrency:
        update_function_concurrency_request, delete_function_concurrency_request = (
            current_lambda.generate_update_function_concurrency_requests(
                desired_aws_lambda
            )
        )

        if update_function_concurrency_request is not None:
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )
            self.put_function_concurrency_raw(
                update_function_concurrency_request
            )
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )
        elif delete_function_concurrency_request is not None:
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )
            self.delete_function_concurrency_raw(
                delete_function_concurrency_request
            )
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )

        # permissions:
        (
            add_permission_requests,
            remove_permission_requests,
        ) = current_lambda.generate_modify_permissions_requests(desired_aws_lambda)

        for update_permission_request in add_permission_requests:
            self.add_permission_raw(update_permission_request)
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )

        for update_permission_request in remove_permission_requests:
            self.remove_permission_raw(update_permission_request)
            self.wait_for_status(
                current_lambda,
                self.update_lambda_information,
                [current_lambda.Status.SUCCESSFUL],
                [current_lambda.Status.INPROGRESS],
                [current_lambda.Status.FAILED],
            )

        if not update_code:
            self.update_lambda_information(desired_aws_lambda, full_information=False)
            return

        update_code_request = current_lambda.generate_update_function_code_request(
            desired_aws_lambda
        )
        if update_code_request is not None:
            self.update_function_code_raw(update_code_request)

        self.update_lambda_information(desired_aws_lambda, full_information=True)

    def put_function_concurrency_raw(self, request_dict):
        """
        Put concurrency.

        :param request_dict:
        :return:
        """

        logger.info(f"Updating concurrency lambda: {request_dict}")

        for response in self.execute(
            self.client.put_function_concurrency, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def delete_function_concurrency_raw(self, request_dict):
        """
        Put concurrency.

        :param request_dict:
        :return:
        """

        logger.info(f"Deleting concurrency lambda: {request_dict}")

        for response in self.execute(
            self.client.delete_function_concurrency, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def provision_lambda_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        log_dict = {key: value for key, value in request_dict.items() if key != "Code"}
        logger.info(f"Creating lambda: {log_dict}")
        for response in self.execute(
            self.client.create_function, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def update_function_code_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        log_dict = {
            key: value for key, value in request_dict.items() if key != "ZipFile"
        }
        logger.info(f"Updating lambda code: {log_dict}")
        for response in self.execute(
            self.client.update_function_code,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            return response

    def update_function_configuration_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Updating lambda configuration: {request_dict}")
        for response in self.execute(
            self.client.update_function_configuration,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            return response

    def remove_permission_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Removing permissions from lambda: {request_dict}")
        for response in self.execute(
            self.client.remove_permission, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def add_permission_raw(self, request_dict):
        """
        Permissions are used to permit different triggers/services to launch this lambda.

        @param request_dict:
        @return:
        """
        logger.info(f"Adding permissions to lambda: {request_dict}")
        for response in self.execute(
            self.client.add_permission, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def provision_event_source_mapping(
        self, event_source_mapping: LambdaEventSourceMapping
    ):
        """
        Standard

        @param event_source_mapping:
        @return:
        """
        region_event_source_mappings = self.get_all_event_source_mappings(
            region=event_source_mapping.region
        )
        for region_event_source_mapping in region_event_source_mappings:
            if not region_event_source_mapping.function_arn.endswith(
                event_source_mapping.function_identification
            ):
                continue
            if (
                region_event_source_mapping.event_source_arn
                != event_source_mapping.event_source_arn
            ):
                continue

            event_source_mapping.update_from_raw_response(
                region_event_source_mapping.dict_src
            )
            return

        AWSAccount.set_aws_region(event_source_mapping.region)
        response = self.provision_event_source_mapping_raw(
            event_source_mapping.generate_create_request()
        )
        del response["ResponseMetadata"]
        event_source_mapping.update_from_raw_response(response)

    def provision_event_source_mapping_raw(self, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Creating lambda event_source_mapping: {request_dict}")
        for response in self.execute(
            self.client.create_event_source_mapping,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            return response

    def invoke_raw(self, request_dict):
        """
        Standard
        request = {"FunctionName": lambda_name, "InvocationType": "DryRun"}

        @param request_dict:
        @return:
        """

        logger.info(f"Invoking lambda: {request_dict}")

        for response in self.execute(
            self.client.invoke, None, raw_data=True, filters_req=request_dict
        ):
            return response
