"""
AWS ec2 client to handle ec2 service API requests.
"""

from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.availability_zone import AvailabilityZone

from horey.aws_api.aws_services_entities.network_interface import NetworkInterface
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.ec2_spot_fleet_request import EC2SpotFleetRequest
from horey.aws_api.aws_services_entities.managed_prefix_list import ManagedPrefixList
from horey.aws_api.aws_services_entities.ami import AMI
from horey.aws_api.aws_services_entities.key_pair import KeyPair
from horey.aws_api.aws_services_entities.internet_gateway import InternetGateway
from horey.aws_api.aws_services_entities.vpc_peering import VPCPeering
from horey.aws_api.aws_services_entities.route_table import RouteTable
from horey.aws_api.aws_services_entities.elastic_address import ElasticAddress
from horey.aws_api.aws_services_entities.nat_gateway import NatGateway

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

    def get_all_subnets(self):
        """
        Get all subnets in all regions.
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for dict_src in self.execute(self.client.describe_subnets, "Subnets"):
                obj = Subnet(dict_src)
                final_result.append(obj)

        return final_result

    def get_all_vpcs(self, region=None):
        """
        Get all interfaces in all regions.
        :return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)
            return self.get_all_vpcs_in_current_region()

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            final_result += self.get_all_vpcs_in_current_region()

        return final_result

    def get_all_vpcs_in_current_region(self):
        final_result = []
        for dict_src in self.execute(self.client.describe_vpcs, "Vpcs"):
            obj = VPC(dict_src)
            final_result.append(obj)
        return final_result
    
    def get_all_availability_zones(self, region=None):
        """
        Get all interfaces in all regions.
        :return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)
            return self.get_all_availability_zones_in_current_region()

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            final_result += self.get_all_availability_zones_in_current_region()

        return final_result

    def get_all_availability_zones_in_current_region(self):
        final_result = []
        for dict_src in self.execute(self.client.describe_availability_zones, "AvailabilityZones"):
            obj = AvailabilityZone(dict_src)
            final_result.append(obj)
        return final_result

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

    def provision_security_group(self, security_group):
        try:
            self.raw_create_security_group(security_group.generate_create_request())
        except Exception as exception_inst:
            repr_exception_inst = repr(exception_inst)
            if "already exists for VPC" not in repr_exception_inst:
                raise
            logger.warning(repr_exception_inst)

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

    def raw_create_managed_prefix_list(self, request, add_client_token=False):
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

    def get_all_managed_prefix_lists(self, full_information=True, region=None):
        if region is not None:
            return self.get_all_managed_prefix_lists_in_region(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_all_managed_prefix_lists_in_region(region, full_information=full_information)
        return final_result

    def get_all_managed_prefix_lists_in_region(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        def _ignore_unsupported_operation_callback(exception_instance):
            exception_message = repr(exception_instance)
            if "UnsupportedOperation" in exception_message and "AWS-managed prefix list" in exception_message:
                return True
            return False

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

    def provision_vpc(self, vpc):
        lst_vpcs = self.get_all_vpcs(region=vpc.region)
        for vpc_exists in lst_vpcs:
            if vpc_exists.get_tagname() == vpc.get_tagname():
                if vpc_exists.cidr_block != vpc.cidr_block:
                    raise RuntimeError(f"VPC {vpc_exists.name} exists with different cidr_block {vpc_exists.cidr_block} != {vpc.cidr_block}")
                return vpc.update_from_raw_create(vpc_exists.dict_src)

        AWSAccount.set_aws_region(vpc.region.region_mark)
        response = self.provision_vpc_raw(vpc.generate_create_request())
        vpc.update_from_raw_create(response)

    def provision_vpc_raw(self, request):
        for response in self.execute(self.client.create_vpc, "Vpc", filters_req=request):
            return response

    def provision_subnets(self, subnets):
        for subnet in subnets:
            try:
                self.provision_subnet_raw(subnet.generate_create_request())
            except Exception as exception_inst:
                if "conflicts with another subnet" in repr(exception_inst):
                    logger.warning(f"{subnet.generate_create_request()}: {repr(exception_inst)}")
                    continue
                raise

    def provision_subnet_raw(self, request):
        for response in self.execute(self.client.create_subnet, "Subnet", filters_req=request):
            return response

    def provision_managed_prefix_list(self, managed_prefix_list):
        lst_objects = self.get_all_managed_prefix_lists(region=managed_prefix_list.region)
        for object_exists in lst_objects:
            if object_exists.get_tagname() == managed_prefix_list.get_tagname():
                managed_prefix_list.id = object_exists.id
                return

        AWSAccount.set_aws_region(managed_prefix_list.region.region_mark)
        response = self.raw_create_managed_prefix_list(managed_prefix_list.generate_create_request())
        managed_prefix_list.update_from_raw_create(response)
    
    def get_all_amis(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_amis(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_amis(region, full_information=full_information)
        return final_result

    def get_region_amis(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_images, "Images"):
            obj = AMI(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result
    
    def get_all_key_pairs(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_key_pairs(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_key_pairs(region, full_information=full_information)
        return final_result

    def get_region_key_pairs(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_key_pairs, "KeyPairs"):
            obj = KeyPair(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result
    
    def get_all_internet_gateways(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_internet_gateways(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_internet_gateways(region, full_information=full_information)
        return final_result

    def get_region_internet_gateways(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_internet_gateways, "InternetGateways"):
            obj = InternetGateway(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def get_all_vpc_peerings(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_vpc_peerings(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_vpc_peerings(region, full_information=full_information)
        return final_result

    def get_region_vpc_peerings(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_vpc_peering_connections, "VpcPeeringConnections"):
            obj = VPCPeering(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result
    
    def get_all_route_tables(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_route_tables(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_route_tables(region, full_information=full_information)
        return final_result

    def get_region_route_tables(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_route_tables, "RouteTables"):
            obj = RouteTable(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result
   
    def get_all_elastic_addresses(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_elastic_addresses(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_elastic_addresses(region, full_information=full_information)
        return final_result

    def get_region_elastic_addresses(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_addresses, "Addresses"):
            obj = ElasticAddress(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result
    
    def get_all_nat_gateways(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_nat_gateways(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_nat_gateways(region, full_information=full_information)
        return final_result

    def get_region_nat_gateways(self, region, full_information=True):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_nat_gateways, "NatGateways"):
            obj = NatGateway(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def provision_internet_gateway(self, internet_gateway):
        """
        create_internet_gateway

        response = client.attach_internet_gateway(
        InternetGatewayId='string',
        VpcId='string'
        )
        """
        attachment_vpc_ids = [att["VpcId"] for att in internet_gateway.attachments]
        try:
            response = self.provision_internet_gateway_raw(internet_gateway.generate_create_request())
            internet_gateway.update_from_raw_response(response)
        except Exception as exception_inst:
            pdb.set_trace()
            if "conflicts with another" not in repr(exception_inst):
                raise
            logger.warning(f"{internet_gateway.generate_create_request()}: {repr(exception_inst)}")

        for attachment in attachment_vpc_ids:
            if attachment["VpcId"] in [att["VpcId"] for att in self.attachments]:
                attachment_vpc_ids.remove(attachment["VpcId"])
        pdb.set_trace()
        for attachment_vpc_id in attachment_vpc_ids:
            request = {"InternetGatewayId": internet_gateway.id, "VpcId": attachment_vpc_id}
            self.attach_internet_gateway_raw(request)

    def provision_internet_gateway_raw(self, request):
        for response in self.execute(self.client.create_internet_gateway, "InternetGateway", filters_req=request):
            return response

    def attach_internet_gateway_raw(self, request):
        for response in self.execute(self.client.attach_internet_gateway, "ResponseMetadata", filters_req=request):
            return response

    def provision_elastic_address(self, elastic_address):
        try:
            self.provision_elastic_address_raw(elastic_address.generate_create_request())
        except Exception as exception_inst:
            repr_exception_inst = repr(exception_inst)
            if "already exists for VPC" not in repr_exception_inst:
                raise
            logger.warning(repr_exception_inst)

    def provision_elastic_address_raw(self, request_dict):
        for response in self.execute(self.client.allocate_address, "", filters_req=request_dict, raw_data=True):
            pdb.set_trace()
            return response
