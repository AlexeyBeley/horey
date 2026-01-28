"""
AWS client to handle service API requests.
"""

import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.servicediscovery_service import (
    ServicediscoveryService,
)
from horey.aws_api.aws_services_entities.servicediscovery_namespace import (
    ServicediscoveryNamespace,
)
from horey.aws_api.aws_services_entities.servicediscovery_instance import (
    ServicediscoveryInstance,
)
from horey.h_logger import get_logger

logger = get_logger()


class ServicediscoveryClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self, aws_account=None):
        client_name = "servicediscovery"
        super().__init__(client_name, aws_account=aws_account)

    def get_all_services(self, region=None):
        """
        Standard

        :return:
        """

        if region:
            return self.get_region_services(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_services(_region)
        return final_result

    def get_region_services(self, region, custom_filters=None):
        """
        Standard

        :param region:
        :param custom_filters:
        :return:
        """
        final_result = []
        if custom_filters is not None:
            custom_filters = {"Filters": custom_filters}

        for response in self.execute(
                self.get_session_client(region=region).list_services, "Services", filters_req=custom_filters
        ):
            obj = ServicediscoveryService(response)
            final_result.append(obj)
            self.update_service_instances(obj)
        return final_result

    def update_service_instances(self, sd_service):
        """
        Standard

        :param sd_service:
        :return:
        """
        filters_req = {"ServiceId": sd_service.id}
        final_result = []

        for response in self.execute(
                self.get_session_client(region=sd_service.region).list_instances, "Instances", filters_req=filters_req
        ):
            obj = ServicediscoveryInstance(response)
            final_result.append(obj)
            sd_service.instances.append(obj)

    def get_all_namespaces(self, region=None):
        """
        Standard

        :param region:
        :return:
        """
        if region is not None:
            return self.get_region_namespaces(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_namespaces(_region)

        return final_result

    def get_region_namespaces(
            self, region, custom_filters=None
    ):
        """
        Standard
        :param region:
        :param custom_filters:
        :return:
        """
        final_result = []
        if custom_filters is not None:
            custom_filters = {"Filters": custom_filters}

        for response in self.execute(
                self.get_session_client(region=region).list_namespaces, "Namespaces", filters_req=custom_filters
        ):
            obj = ServicediscoveryNamespace(response)
            final_result.append(obj)

        return final_result

    def update_namespace_information(self, namespace):
        """
        Standard

        :param namespace:
        :return:
        """
        custom_filters = [
            {"Name": "TYPE", "Values": [namespace.type], "Condition": "EQ"}
        ]
        region_namespaces = self.get_region_namespaces(
            namespace.region, custom_filters=custom_filters
        )
        for region_namespace in region_namespaces:
            if region_namespace.name == namespace.name:
                namespace.update_from_raw_response(region_namespace.dict_src)
                return True

        return False

    def update_service_information(self, service):
        """
        Standard

        :param service:
        :return:
        """

        if service.namespace_id is None:
            raise RuntimeError(
                f"Can not find service without namespace_id been set: {service.name}"
            )

        custom_filters = [
            {
                "Name": "NAMESPACE_ID",
                "Values": [service.namespace_id],
                "Condition": "EQ",
            }
        ]

        region_services = self.get_region_services(
            service.region, custom_filters=custom_filters
        )
        for region_service in region_services:
            if region_service.name == service.name:
                service.update_from_raw_response(region_service.dict_src)
                return True

        return False

    def provision_namespace(self, namespace: ServicediscoveryNamespace):
        """
        create_namespace
        """
        if self.update_namespace_information(namespace):
            return True

        try:
            if namespace.type == "DNS_PRIVATE":
                operation_id = self.provision_private_namespace_raw(namespace.region,
                                                                    namespace.generate_create_request()
                                                                    )
            else:
                raise NotImplementedError(namespace.type)

            self.wait_for_operation_success(namespace.region, operation_id)
            return self.update_namespace_information(namespace)
        except Exception as exception_inst:
            logger.warning(
                f"{namespace.generate_create_request()}: {repr(exception_inst)}"
            )
            raise

    def provision_private_namespace_raw(self, region, request):
        """
        Standard

        :param region:
        :param request:
        :return:
        """
        for operation_id in self.execute(
                self.get_session_client(region=region).create_private_dns_namespace, "OperationId", filters_req=request
        ):
            return operation_id

    def provision_service(self, service: ServicediscoveryService):
        """
        create_service
        """
        if self.update_service_information(service):
            return True

        try:
            response = self.provision_service_raw(service.region, service.generate_create_request())
            service.update_from_raw_response(response)

            return self.update_service_information(service)
        except Exception as exception_inst:
            logger.warning(
                f"{service.generate_create_request()}: {repr(exception_inst)}"
            )
            raise

    def provision_service_raw(self, region, request):
        """
        Standard

        :param region:
        :param request:
        :return:
        """
        for response in self.execute(
                self.get_session_client(region=region).create_service, "Service", filters_req=request
        ):
            return response

    def wait_for_operation_success(self, region, operation_id):
        """
        Standard

        :param region:
        :param operation_id:
        :return:
        """
        time_wait = 300
        sleep_interval = 5
        for _ in range(time_wait // sleep_interval):
            for status_response in self.execute(
                    self.get_session_client(region=region).get_operation,
                    "Operation",
                    filters_req={"OperationId": operation_id},
            ):
                if status_response["Status"] in ["SUBMITTED", "PENDING"]:
                    time.sleep(sleep_interval)
                elif status_response["Status"] == "SUCCESS":
                    break
                elif status_response["Status"] == "FAIL":
                    raise RuntimeError(status_response)
            else:
                continue
            break
        else:
            raise TimeoutError(time_wait)
