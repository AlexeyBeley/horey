"""
AWS clietn to handle service API requests.
"""
import pdb

import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.servicediscovery_service import ServicediscoveryService
from horey.aws_api.aws_services_entities.servicediscovery_namespace import ServicediscoveryNamespace
from horey.aws_api.aws_services_entities.servicediscovery_instance import ServicediscoveryInstance
from horey.h_logger import get_logger


logger = get_logger()


class ServicediscoveryClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "servicediscovery"
        super().__init__(client_name)

    def get_all_services(self, full_information=True):
        final_result = []
        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)

            for response in self.execute(self.client.list_services, "Services"):
                obj = ServicediscoveryService(response)
                final_result.append(obj)
                self.update_service_instances(obj)

        return final_result

    def update_service_instances(self, sd_service):
        filters_req = {"ServiceId": sd_service.id}
        final_result = []

        for response in self.execute(self.client.list_instances, "Instances", filters_req=filters_req):
            obj = ServicediscoveryInstance(response)
            final_result.append(obj)
            sd_service.instances.append(obj)

    def get_all_namespaces(self, region=None, full_information=True):
        if region is not None:
            return self.get_region_namespaces(region, full_information=full_information)

        final_result = []
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_namespaces(region)

        return final_result

    def get_region_namespaces(self, region, full_information=False, custom_filters=None):
        AWSAccount.set_aws_region(region)
        final_result = []
        for response in self.execute(self.client.list_namespaces, "Namespaces"):
            obj = ServicediscoveryNamespace(response)
            final_result.append(obj)

        return final_result

    def update_namespace_information(self, namespace):
        custom_filters = [{"Name": "Name", "Values": [namespace.name], "Condition": "EQ"}]
        region_namespace = self.get_region_namespaces(namespace.region, custom_filters=custom_filters)

        if len(region_namespace) == 1:
            namespace.update_from_raw_response(region_namespace[0].dict_src)
            return True
        elif len(region_namespace) > 1:
            raise RuntimeError(f"Expected single namespace, found {len(region_namespace)}")
        return False

    def provision_namespace(self, namespace: ServicediscoveryNamespace):
        """
        create_namespace
        """
        if self.update_namespace_information(namespace):
            return

        try:
            if namespace.type == "DNS_PRIVATE":
                operation_id = self.provision_private_namespace_raw(namespace.generate_create_request())
            else:
                raise NotImplementedError(namespace.type)

            self.wait_for_operation_success(operation_id)
            return self.update_namespace_information(namespace)
        except Exception as exception_inst:
            logger.warning(f"{namespace.generate_create_request()}: {repr(exception_inst)}")
            raise

    def provision_private_namespace_raw(self, request):
        for operation_id in self.execute(self.client.create_private_dns_namespace, "OperationId", filters_req=request):
            return operation_id

    def wait_for_operation_success(self, operation_id):
        time_wait = 300
        sleep_interval = 5
        for counter in range(time_wait//sleep_interval):
            for status_response in self.execute(self.client.get_operation, "Operation", filters_req={"OperationId": operation_id}):
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


