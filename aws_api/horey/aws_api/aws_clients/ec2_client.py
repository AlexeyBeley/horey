"""
AWS ec2 client to handle ec2 service API requests.
"""
import time
import base64
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.availability_zone import AvailabilityZone

from horey.aws_api.aws_services_entities.network_interface import NetworkInterface
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.ec2_launch_template_version import EC2LaunchTemplateVersion
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
from horey.common_utils.common_utils import CommonUtils
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

    def get_all_subnets(self, region=None):
        """
        Get all subnets in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_subnets(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_subnets(region)

        return final_result

    def get_region_subnets(self, region, filters=None):
        final_result = list()
        filters_req = dict()
        if filters is not None:
            filters_req["Filters"] = filters
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_subnets, "Subnets", filters_req=filters_req):
            obj = Subnet(dict_src)
            final_result.append(obj)

        return final_result

    def get_all_vpcs(self, region=None):
        """
        Get all interfaces in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_vpcs(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_vpcs(region)

        return final_result

    def get_region_vpcs(self, region, filters=None):
        AWSAccount.set_aws_region(region)
        final_result = []
        filters_req = dict()
        if filters is not None:
            filters_req["Filters"] = filters

        for dict_src in self.execute(self.client.describe_vpcs, "Vpcs", filters_req=filters_req):
            obj = VPC(dict_src)
            obj.region = region
            final_result.append(obj)
        return final_result

    def init_vpc_attributes(self, vpc):
        pdb.set_trace()
        for attr_name in ["EnableDnsHostnames", "EnableDnsSupport"]:
            for value in self.execute(self.client.describe_vpc_attribute, attr_name, filters_req={"Attribute": attr_name, "VpcId":vpc.id}):
                vpc.init_default_attr(attr_name, value)

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

    def get_all_instances(self, region=None):
        """
        Get all ec2 instances in current region.
        :return:
        """

        if region is not None:
            return self.get_region_instances(region)

        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_instances(region)

        return final_result

    def get_region_instances(self, region, filters=None):
        AWSAccount.set_aws_region(region)
        final_result = []

        if filters is not None:
            filters_req = {"Filters": filters}
        else:
            filters_req = None

        for instance in self.execute(self.client.describe_instances, "Reservations", filters_req=filters_req):
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

    def get_region_security_groups(self, region, full_information=True, filters=None):
        AWSAccount.set_aws_region(region)
        final_result = list()
        filters_req = dict()
        if filters is not None:
            filters_req["Filters"] = filters
        for ret in self.execute(self.client.describe_security_groups, "SecurityGroups", filters_req=filters_req):
            obj = EC2SecurityGroup(ret)
            if full_information is True:
                raise NotImplementedError()

            final_result.append(obj)

        return final_result

    def provision_security_group(self, security_group):
        try:
            group_id = self.raw_create_security_group(security_group.generate_create_request())
            security_group.id = group_id
            # wait for propagation?
            #for i in range(60):
            #    region_groups = self.get_all_security_groups_in_region(security_group.region, full_information=False)
            #    named_region_groups = CommonUtils.find_objects_by_values(region_groups, {"name": security_group.name}, max_count=1)
            #    if len(named_region_groups) > 0:
            #        break
            #    time.sleep(5)
        except Exception as exception_inst:
            repr_exception_inst = repr(exception_inst)
            if "already exists for VPC" not in repr_exception_inst:
                raise
            logger.warning(repr_exception_inst)
            region_groups = self.get_region_security_groups(security_group.region, full_information=False)
            existing_group = CommonUtils.find_objects_by_values(region_groups, {"name": security_group.name}, max_count=1)[0]
            security_group.update_from_raw_create(existing_group.dict_src)

    def raw_create_security_group(self, request_dict):
        logger.info(f"Creating security group {request_dict}")
        for group_id in self.execute(self.client.create_security_group, "GroupId", filters_req=request_dict):
            return group_id

    def authorize_security_group_ingress(self, region, request_dict):
        AWSAccount.set_aws_region(region)
        try:
            return self.authorize_security_group_ingress_raw(request_dict)
        except Exception as inst_exception:
            if "already exists" in repr(inst_exception):
                for request_ip_permission in request_dict["IpPermissions"]:
                    request_dict_tmp = {"GroupId": request_dict["GroupId"],
                                        "IpPermissions": [request_ip_permission]}

                    self.authorize_security_group_ingress_raw(request_dict_tmp, ignore_exists=True)
            else:
                raise

    def authorize_security_group_ingress_raw(self, request_dict, ignore_exists=False):
        logger.info(f"Authorizing security group ingress: {request_dict}")
        if ignore_exists:
            for response in self.execute(self.client.authorize_security_group_ingress, "GroupId", filters_req=request_dict,
                                    raw_data=True, exception_ignore_callback=lambda x: "already exists" in repr(x)):
                return response
        else:
            for response in self.execute(self.client.authorize_security_group_ingress, "GroupId", filters_req=request_dict,
                             raw_data=True):
                return response

    def create_instance(self, request_dict):
        for response in self.execute(self.client.run_instances, "Instances", filters_req=request_dict):
            return response

    def create_key_pair(self, request_dict):
        for response in self.execute(self.client.create_key_pair, None, raw_data=True, filters_req=request_dict):
            return response

    def provision_launch_template_raw(self, request_dict):
        logger.info(f"Creating Launch Template: {request_dict}")
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

    def get_all_ec2_launch_templates(self, full_information=False, region=None):
        final_result = list()

        if region is not None:
            return self.get_region_launch_templates(region, full_information=full_information)

        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_launch_templates(region, full_information=full_information)

        return final_result

    def get_region_launch_templates(self, region, full_information=False):
        AWSAccount.set_aws_region(region)
        final_result = list()
        logger.info(f"Fetching all launch templates from {region}")
        for ret in self.execute(self.client.describe_launch_templates, "LaunchTemplates"):
            obj = EC2LaunchTemplate(ret)
            obj.region = region
            if full_information is True:
                raise NotImplementedError()

            final_result.append(obj)
        return final_result

    def get_all_launch_template_versions(self, launch_template):
        """
        Get all launch_template_versions in all regions.
        :return:
        """

        final_result = []
        filters_req = {"LaunchTemplateId": launch_template.id}
        AWSAccount.set_aws_region(launch_template.region)
        for dict_src in self.execute(self.client.describe_launch_template_versions, "LaunchTemplateVersions", filters_req=filters_req):
            obj = EC2LaunchTemplateVersion(dict_src)
            final_result.append(obj)

        return final_result
    
    def get_security_group(self, security_group):
        if security_group.id is not None:
            filters_req = {"GroupIds": [security_group.id]}
            for x in self.execute(self.client.describe_security_groups, "SecurityGroups", filters_req=filters_req):
                pdb.set_trace()
        elif security_group.name is not None:
            AWSAccount.set_aws_region(security_group.region)
            vpc_filter = {'Name': 'vpc-id', 'Values': [security_group.vpc_id]}
            filters_req = {"GroupNames": [security_group.name], "Filters": [vpc_filter]}
            pdb.set_trace()
            for response in self.execute(self.client.describe_security_groups, "SecurityGroups", filters_req=filters_req):
                pdb.set_trace()
        else:
            raise NotImplementedError()

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

    def get_managed_prefix_list(self, region, pl_id=None, name=None, full_information=True):
        response = self.raw_describe_managed_prefix_list(region, pl_id=pl_id, prefix_list_name=name)
        obj = ManagedPrefixList(response)
        if full_information:
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
            if vpc_exists.get_tagname(ignore_missing_tag=True) == vpc.get_tagname():
                if vpc_exists.cidr_block != vpc.cidr_block:
                    raise RuntimeError(f"VPC {vpc_exists.name} exists with different cidr_block {vpc_exists.cidr_block} != {vpc.cidr_block}")
                vpc.id = vpc_exists.id

        if vpc.id is None:
            AWSAccount.set_aws_region(vpc.region.region_mark)
            response = self.provision_vpc_raw(vpc.generate_create_request())
            vpc.id = response["VpcId"]

        for request in vpc.generate_modify_vpc_attribute_requests():
            self.modify_vpc_attribute_raw(request)

    def provision_vpc_raw(self, request):
        for response in self.execute(self.client.create_vpc, "Vpc", filters_req=request):
            return response

    def modify_vpc_attribute_raw(self, request):
        logger.info(f"Modifying VPC {request}")
        for response in self.execute(self.client.modify_vpc_attribute, None, filters_req=request, raw_data=True):
            return response

    def provision_subnets(self, subnets):
        """

        """
        for subnet in subnets[1:]:
            if subnet.region.region_mark != subnets[0].region.region_mark:
                raise RuntimeError("All subnets should be in one region")

        region_subnets = self.get_region_subnets(subnets[0].region)
        for subnet in subnets:
            for region_subnet in region_subnets:
                if region_subnet.get_tagname(ignore_missing_tag=True) == subnet.get_tagname():
                    if region_subnet.cidr_block != subnet.cidr_block:
                        raise RuntimeError(
                        f"Subnet {subnet.get_tagname()} exists with different cidr_block {region_subnet.cidr_block} != {subnet.cidr_block}")
                    subnet.update_from_raw_create(region_subnet.dict_src)

        for subnet in subnets:
            if subnet.id is not None:
                continue
            try:
                response = self.provision_subnet_raw(subnet.generate_create_request())
                subnet.id = response["SubnetId"]
            except Exception as exception_inst:
                if "conflicts with another subnet" in repr(exception_inst):
                    logger.warning(f"{subnet.generate_create_request()}: {repr(exception_inst)}")
                    continue
                raise

    def provision_subnet_raw(self, request):
        for response in self.execute(self.client.create_subnet, "Subnet", filters_req=request):
            return response

    def provision_managed_prefix_list(self, managed_prefix_list):
        raw_region_pl = self.raw_describe_managed_prefix_list(managed_prefix_list.region, prefix_list_name=managed_prefix_list.name)

        if raw_region_pl is None:
            AWSAccount.set_aws_region(managed_prefix_list.region.region_mark)
            response = self.raw_create_managed_prefix_list(managed_prefix_list.generate_create_request())
            managed_prefix_list.update_from_raw_create(response)
            return

        region_object = ManagedPrefixList(raw_region_pl)
        self.update_managed_prefix_list_full_information(region_object)

        request = region_object.get_entries_add_request(managed_prefix_list)
        if request is not None:
            # todo: optimize - use return value
            self.raw_modify_managed_prefix_list(request)
            raw_region_pl = self.raw_describe_managed_prefix_list(managed_prefix_list.region, prefix_list_name=managed_prefix_list.name)

        managed_prefix_list.update_from_raw_create(raw_region_pl)

    def get_all_amis(self, full_information=True, region=None):
        if region is not None:
            return self.get_region_amis(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_amis(region, full_information=full_information)
        return final_result

    def get_region_amis(self, region, full_information=True, custom_filters=None):
        AWSAccount.set_aws_region(region)
        final_result = list()

        for response in self.execute(self.client.describe_images, "Images", filters_req=custom_filters):
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
        region_gateways = self.get_region_internet_gateways(internet_gateway.region)
        for region_gateway in region_gateways:
            if region_gateway.get_tagname(ignore_missing_tag=True) == internet_gateway.get_tagname():
                internet_gateway.id = region_gateway.id
                break

        if internet_gateway.id is None:
            try:
                response = self.provision_internet_gateway_raw(internet_gateway.generate_create_request())
                internet_gateway.id = response["InternetGatewayId"]
                region_gateway = InternetGateway(response)
            except Exception as exception_inst:
                logger.warning(f"{internet_gateway.generate_create_request()}: {repr(exception_inst)}")
                raise

        attachment_vpc_ids = [att["VpcId"] for att in internet_gateway.attachments]
        for vpc_id in attachment_vpc_ids:
            if vpc_id in [att["VpcId"] for att in region_gateway.attachments]:
                attachment_vpc_ids.remove(vpc_id)

        for attachment_vpc_id in attachment_vpc_ids:
            request = {"InternetGatewayId": internet_gateway.id, "VpcId": attachment_vpc_id}
            self.attach_internet_gateway_raw(request)

    def provision_internet_gateway_raw(self, request):
        for response in self.execute(self.client.create_internet_gateway, "InternetGateway", filters_req=request):
            return response

    def attach_internet_gateway_raw(self, request):
        logger.info(request)
        for response in self.execute(self.client.attach_internet_gateway, "ResponseMetadata", filters_req=request):
            return response

    def provision_elastic_address(self, elastic_address):
        region_elastic_addresses = self.get_region_elastic_addresses(elastic_address.region)
        for region_elastic_address in region_elastic_addresses:
            if region_elastic_address.get_tagname(ignore_missing_tag=True) == elastic_address.get_tagname():
                elastic_address.update_from_raw_response(region_elastic_address.dict_src)
                return
                
        try:
            response = self.provision_elastic_address_raw(elastic_address.generate_create_request())
            del response["ResponseMetadata"]
            elastic_address.update_from_raw_response(response)
        except Exception as exception_inst:
            repr_exception_inst = repr(exception_inst)
            logger.warning(repr_exception_inst)
            raise

    def provision_elastic_address_raw(self, request_dict):
        for response in self.execute(self.client.allocate_address, "", filters_req=request_dict, raw_data=True):
            return response

    def provision_vpc_peering(self, vpc_peering):
        region_vpc_peerings = self.get_region_vpc_peerings(vpc_peering.region)
        for region_vpc_peering in region_vpc_peerings:
            if region_vpc_peering.get_status() in [region_vpc_peering.Status.DELETED, region_vpc_peering.Status.DELETING]:
                continue
            if region_vpc_peering.get_tagname(ignore_missing_tag=True) != vpc_peering.get_tagname():
                continue

            vpc_peering.update_from_raw_response(region_vpc_peering.dict_src)

            if region_vpc_peering.get_status() in [region_vpc_peering.Status.ACTIVE, region_vpc_peering.Status.PROVISIONING]:
                return
            break

        if vpc_peering.id is None:
            AWSAccount.set_aws_region(vpc_peering.region)
            response = self.provision_vpc_peering_raw(vpc_peering.generate_create_request())
            vpc_peering.update_from_raw_response(response)

        if vpc_peering.get_status() in [vpc_peering.Status.INITIATING_REQUEST, vpc_peering.Status.PENDING_ACCEPTANCE]:
            AWSAccount.set_aws_region(vpc_peering.peer_region)
            for counter in range(20):
                try:
                    self.accept_vpc_peering_connection_raw(vpc_peering.generate_accept_request())
                    break
                except Exception as exception_inst:
                    repr_exception_inst = repr(exception_inst)
                    if "does not exist" not in repr_exception_inst:
                        raise
                time.sleep(5)
        else:
            raise RuntimeError(vpc_peering.get_status())

    def provision_vpc_peering_raw(self, request_dict):
        logger.info(f"Creating VPC Peering: {request_dict}")
        for response in self.execute(self.client.create_vpc_peering_connection, "VpcPeeringConnection", filters_req=request_dict):
            return response

    def accept_vpc_peering_connection_raw(self, request_dict):
        for response in self.execute(self.client.accept_vpc_peering_connection, "VpcPeeringConnection", filters_req=request_dict):
            return response

    def provision_launch_template(self, launch_template):
        region_objects = self.get_region_launch_templates(launch_template.region)
        for region_object in region_objects:
            if region_object.name == launch_template.name:
                launch_template.update_from_raw_response(region_object.dict_src)
                return

        AWSAccount.set_aws_region(launch_template.region)
        response = self.provision_launch_template_raw(launch_template.generate_create_request())
        launch_template.update_from_raw_response(response)

    def provision_nat_gateway(self, nat_gateway):
        region_gateways = self.get_region_nat_gateways(nat_gateway.region)
        for region_gateway in region_gateways:
            if region_gateway.get_state() not in [region_gateway.State.AVAILABLE, region_gateway.State.PENDING]:
                continue
            if region_gateway.get_tagname(ignore_missing_tag=True) == nat_gateway.get_tagname():
                nat_gateway.update_from_raw_response(region_gateway.dict_src)
                return

        try:
            response = self.provision_nat_gateway_raw(nat_gateway.generate_create_request())
            nat_gateway.update_from_raw_response(response)
        except Exception as exception_inst:
            logger.warning(repr(exception_inst))
            raise

    def provision_nat_gateway_raw(self, request_dict):
        for response in self.execute(self.client.create_nat_gateway, "NatGateway", filters_req=request_dict):
            return response
    
    def provision_route_table(self, route_table):
        region_route_tables = self.get_region_route_tables(route_table.region)
        for region_route_table in region_route_tables:
            if region_route_table.get_tagname(ignore_missing_tag=True) == route_table.get_tagname():
                route_table.id = region_route_table.id
                break
        else:
            try:
                response = self.provision_route_table_raw(route_table.generate_create_request())
                route_table.id = response["RouteTableId"]
            except Exception as exception_inst:
                logger.warning(repr(exception_inst))
                raise

        try:
            self.associate_route_table_raw(route_table.generate_associate_route_table_request())
        except Exception as exception_inst:
            logger.warning(repr(exception_inst))
            raise

        self.create_routes(route_table)

    def create_routes(self, route_table, replace=True):
        AWSAccount.set_aws_region(route_table.region)
        for request in route_table.generate_create_route_requests():
            try:
                self.create_route_raw(request)
            except Exception as exception_inst:
                repr_exception_inst = repr(exception_inst)
                logger.warning(repr_exception_inst)
                if "already exists" not in repr_exception_inst:
                    raise
                if replace:
                    self.replace_route_raw(request)

    def provision_route_table_raw(self, request_dict):
        for response in self.execute(self.client.create_route_table, "RouteTable", filters_req=request_dict):
            return response

    def associate_route_table_raw(self, request_dict):
        logger.info(f"Associating route table: {request_dict}")
        for response in self.execute(self.client.associate_route_table, "AssociationId", filters_req=request_dict):
            return response

    def create_route_raw(self, request_dict):
        logger.info(f"Creating route {request_dict}")
        for response in self.execute(self.client.create_route, "Return", filters_req=request_dict):
            return response

    def replace_route_raw(self, request_dict):
        logger.info(f"Replacing route {request_dict}")
        for response in self.execute(self.client.replace_route, None, filters_req=request_dict, raw_data=True):
            return response

    def get_region_ec2_instances(self, region):
        AWSAccount.set_aws_region(region)
        final_result = list()
        for instance in self.execute(self.client.describe_instances, "Reservations"):
            final_result.extend(instance['Instances'])
        return [EC2Instance(instance) for instance in final_result]
    
    def provision_ec2_instance(self, ec2_instance):
        region_ec2_instances = self.get_region_ec2_instances(ec2_instance.region)
        for region_ec2_instance in region_ec2_instances:
            if region_ec2_instance.get_state() not in [region_ec2_instance.State.RUNNING, region_ec2_instance.State.PENDING]:
                continue

            if region_ec2_instance.get_tagname(ignore_missing_tag=True) == ec2_instance.get_tagname():
                ec2_instance.update_from_raw_response(region_ec2_instance.dict_src)
                return

        try:
            response = self.provision_ec2_instance_raw(ec2_instance.generate_create_request())
            ec2_instance.update_from_raw_response(response)
        except Exception as exception_inst:
            logger.warning(repr(exception_inst))
            raise

    def provision_ec2_instance_raw(self, request_dict):
        for response in self.execute(self.client.run_instances, "Instances", filters_req=request_dict):
            return response
    
    def provision_key_pair(self, key_pair):
        region_key_pairs = self.get_region_key_pairs(key_pair.region)
        for region_key_pair in region_key_pairs:
            if region_key_pair.name == key_pair.name:
                key_pair.id = region_key_pair.id
                return

        try:
            return self.provision_key_pair_raw(key_pair.generate_create_request())
        except Exception as exception_inst:
            logger.warning(repr(exception_inst))
            raise

    def provision_key_pair_raw(self, request_dict):
        for response in self.execute(self.client.create_key_pair, None, filters_req=request_dict, raw_data=True):
            return response

    def test_debug(self):
        import pdb
        ret_1 = self.get_region_amis("us-west-2")
        ret_syd = self.get_region_amis("ap-southeast-2")
        syd_ami = self.get_region_amis("ap-southeast-2", image_ids=["ami-0f39d06d145e9bb63"])

        pdb.set_trace()
        for response in self.execute(self.client.describe_managed_prefix_lists, "PrefixLists", filters_req=request):
            return response

    def associate_elastic_address_raw(self, request_dict):
        for response in self.execute(self.client.associate_address, None, filters_req=request_dict, raw_data=True):
            return response

    @staticmethod
    def generate_user_data_from_file(file_path):
        with open(file_path) as file_handler:
            user_data = file_handler.read()
        return base64.b64encode(user_data.encode()).decode("ascii")
