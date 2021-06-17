"""
AWS ec2 client to handle ec2 service API requests.
"""

from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.network_interface import NetworkInterface
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.ec2_spot_fleet_request import EC2SpotFleetRequest
from horey.aws_api.aws_services_entities.managed_prefix_list import ManagedPrefixList
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
import pdb

from horey.h_logger import get_logger

logger = get_logger()

class EC2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ec2"
        super().__init__(client_name)

    def get_all_interfaces(self):
        """
        Get all interfaces in all regions.
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for dict_src in self.execute(self.client.describe_network_interfaces, "NetworkInterfaces"):
                interface = NetworkInterface(dict_src)
                final_result.append(interface)

        return final_result

    def get_all_instances(self):
        """
        Get all ec2 instances in current region.
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for instance in self.execute(self.client.describe_instances, "Reservations"):
                final_result.extend(instance['Instances'])
        return [EC2Instance(instance) for instance in final_result]

    def get_all_security_groups(self, full_information=False):
        """
        Get all security groups in the region.
        :param full_information:
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for ret in self.execute(self.client.describe_security_groups, "SecurityGroups"):
                obj = EC2SecurityGroup(ret)
                if full_information is True:
                    raise NotImplementedError()

                final_result.append(obj)

        return final_result

    def raw_create_security_group(self, request_dict):
        for response in self.execute(self.client.create_security_group, "GroupId", filters_req=request_dict):
            return response

    def authorize_security_group_ingress(self, request_dict):
        for response in self.execute(self.client.authorize_security_group_ingress, "GroupId", filters_req=request_dict,
                                     raw_data=True):
            print(response)
            return response

    def create_instance(self, request_dict):
        for response in self.execute(self.client.run_instances, "Instances", filters_req=request_dict):
            with open("/tmp/instances.txt", "a+") as file_handler:
                file_handler.write(f"{response['InstanceId']}\n")
            print(response["InstanceId"])
            return response

    def create_key_pair(self, request_dict):
        for response in self.execute(self.client.create_key_pair, None, raw_data=True, filters_req=request_dict):
            return response

    def create_launch_template(self, request_dict):
        for response in self.execute(self.client.create_launch_template, "LaunchTemplate", filters_req=request_dict):
            return response

    def request_spot_fleet(self, request_dict):
        for response in self.execute(self.client.request_spot_fleet, "SpotFleetRequestId", filters_req=request_dict):
            return response

    def get_all_spot_fleet_requests(self, full_information=False):
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for ret in self.execute(self.client.describe_spot_fleet_requests, "SpotFleetRequestConfigs"):
                obj = EC2SpotFleetRequest(ret)
                if full_information is True:
                    raise NotImplementedError()

                final_result.append(obj)

        return final_result

    def get_all_ec2_launch_templates(self, full_information=False):
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for ret in self.execute(self.client.describe_launch_templates, "LaunchTemplates"):
                obj = EC2LaunchTemplate(ret)
                if full_information is True:
                    raise NotImplementedError()

                final_result.append(obj)

        return final_result

    def update_security_group(self, security_group):
        filters_req = {"GroupId": security_group.id,
                       "IpPermissions": security_group.generate_permissions_request_dict()
                       }

        for x in self.execute(self.client.authorize_security_group_ingress, None, filters_req=filters_req):
            pdb.set_trace()

    def raw_create_managed_prefix_list(self, request, add_client_token=True):
        if add_client_token:
            if "ClientToken" not in request:
                request["ClientToken"] = request["PrefixListName"]

        for response in self.execute(self.client.create_managed_prefix_list, "PrefixList", filters_req=request):
            return response

    def raw_modify_managed_prefix_list(self, request):
        logger.info(f"Modifying prefix list with request: {request}")
        try:
            for response in self.execute(self.client.modify_managed_prefix_list, "PrefixList", filters_req=request):
                return response
        except Exception as exception_instance:
            if "already exists" not in repr(exception_instance):
                raise

            logger.info(repr(exception_instance))

    def raw_describe_managed_prefix_list(self, region, pl_id=None, prefix_list_name=None):
        AWSAccount.set_aws_region(region)
        if pl_id is None and prefix_list_name is None:
            raise ValueError("pl_id pr prefix_list_name must be specified")

        request = {}
        if pl_id is not None:
            request["PrefixListIds"] = [pl_id]

        if prefix_list_name is not None:
            request["Filters"] = [{
                'Name': 'prefix-list-name',
                'Values': [prefix_list_name]
            }]

        for response in self.execute(self.client.describe_managed_prefix_lists, "PrefixLists", filters_req=request):
            return response

    def get_managed_prefix_list(self, region, pl_id):
        response = self.raw_describe_managed_prefix_list(region, pl_id=pl_id)
        obj = ManagedPrefixList(response)
        self.update_managed_prefix_list_full_information(obj)
        return obj

    def update_managed_prefix_list_full_information(self, prefix_list):
        filters_req = {"PrefixListId": prefix_list.id}
        for associations_response in self.execute(self.client.get_managed_prefix_list_associations,
                                                  "PrefixListAssociations", filters_req=filters_req):
            prefix_list.add_association_from_raw_response(associations_response)

        for entries_response in self.execute(self.client.get_managed_prefix_list_entries, "Entries",
                                             filters_req=filters_req):
            prefix_list.add_entry_from_raw_response(entries_response)

    def get_all_managed_prefix_lists(self, full_information=True):
        final_result = list()

        def _ignore_unsupported_operation_callback(exception_instance):
            exception_message = repr(exception_instance)
            if "UnsupportedOperation" in exception_message and "AWS-managed prefix list" in exception_message:
                return True
            return False

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for response in self.execute(self.client.describe_managed_prefix_lists, "PrefixLists"):
                obj = ManagedPrefixList(response)
                if full_information is True:
                    # todo: replace with update_managed_prefix_list_full_information
                    filters_req = {"PrefixListId": obj.id}
                    for associations_response in self.execute(self.client.get_managed_prefix_list_associations, "PrefixListAssociations", filters_req=filters_req, exception_ignore_callback=_ignore_unsupported_operation_callback):
                        obj.add_association_from_raw_response(associations_response)

                    for entries_response in self.execute(self.client.get_managed_prefix_list_entries, "Entries", filters_req=filters_req):
                        obj.add_entry_from_raw_response(entries_response)

                final_result.append(obj)

        return final_result
