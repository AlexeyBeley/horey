"""
AWS clietn to handle service API requests.
"""
import pdb


from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.servicediscovery_service import ServicediscoveryService
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
