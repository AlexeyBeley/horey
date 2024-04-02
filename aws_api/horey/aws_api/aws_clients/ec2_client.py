"""
AWS ec2 client to handle ec2 service API requests.
"""
# pylint: disable=too-many-lines
import datetime

import time
import base64

from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.ec2_instance_type import EC2InstanceType
from horey.aws_api.aws_services_entities.ec2_volume import EC2Volume
from horey.aws_api.aws_services_entities.ec2_volume_modification import EC2VolumeModification
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.availability_zone import AvailabilityZone

from horey.aws_api.aws_services_entities.network_interface import NetworkInterface
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.ec2_launch_template_version import (
    EC2LaunchTemplateVersion,
)
from horey.aws_api.aws_services_entities.ec2_spot_fleet_request import (
    EC2SpotFleetRequest,
)
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
from horey.aws_api.base_entities.region import Region

from horey.h_logger import get_logger

logger = get_logger()


class EC2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ec2"
        super().__init__(client_name)

    def yield_subnets(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all subnets.

        :return:
        """

        regional_fetcher_generator = self.yield_subnets_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  Subnet,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield obj

    def yield_subnets_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_subnets, "Subnets", filters_req=filters_req
        ):
            yield dict_src

    def get_all_subnets(self, region=None, filters_req=None, update_info=False):
        """
        Get all subnets in all regions.
        :return:
        """

        return list(self.yield_subnets(region=region, filters_req=filters_req, update_info=update_info))

    def get_region_subnets(self, region, filters=None, filters_req=None):
        """
        Get region subnets.

        @param region:
        @param filters:
        @param filters_req:
        @return:
        """

        if filters is not None:
            logger.error("DEPRECATED, use filters_req instead")
            if filters_req is None:
                filters_req = {}
            filters_req["Filters"] = filters

        return list(self.yield_subnets(region=region, filters_req=filters_req))

    def get_all_vpcs(self, region=None, filters=None):
        """
        Get all interfaces in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_vpcs(region, filters=filters)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_vpcs(_region, filters=filters)

        return final_result

    def get_region_vpcs(self, region, filters=None):
        """
        Standard

        @param region:
        @param filters:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []
        filters_req = {}
        if filters is not None:
            filters_req["Filters"] = filters

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_vpcs, "Vpcs", filters_req=filters_req
        ):
            obj = VPC(dict_src)
            obj.region = region
            final_result.append(obj)
        return final_result

    def init_vpc_attributes(self, vpc, region=None):
        """
        Init DNS attributes.

        @param vpc:
        @return:
        :param region:
        """

        for attr_name in ["EnableDnsHostnames", "EnableDnsSupport"]:
            for value in self.execute(
                    self.get_session_client(region=region).describe_vpc_attribute,
                    attr_name,
                    filters_req={"Attribute": attr_name, "VpcId": vpc.id},
            ):
                vpc.init_default_attr(attr_name, value)

    def get_all_availability_zones(self, region=None):
        """
        Get all interfaces in all regions.
        :return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)
            return self.get_all_availability_zones_in_current_region()

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(_region)
            final_result += self.get_all_availability_zones_in_current_region()

        return final_result

    def get_all_availability_zones_in_current_region(self, region=None):
        """
        Standard

        @return:
        """

        final_result = []
        for dict_src in self.execute(
                self.get_session_client(region=region).describe_availability_zones, "AvailabilityZones"
        ):
            obj = AvailabilityZone(dict_src)
            final_result.append(obj)
        return final_result

    def yield_network_interfaces(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all volumes.

        :return:
        """

        regional_fetcher_generator = self.yield_network_interfaces_raw
        for dict_src in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  NetworkInterface,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield dict_src

    def yield_network_interfaces_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_network_interfaces, "NetworkInterfaces", filters_req=filters_req
        ):
            yield dict_src

    def get_all_interfaces(self, region=None, update_info=False):
        """
        Get all interfaces in all regions.

        :return:
        """

        return list(self.yield_network_interfaces(region=region, update_info=update_info))

    def yield_instances(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all volumes.

        :return:
        """

        regional_fetcher_generator = self.yield_instances_raw
        for dict_src in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  EC2Instance,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield dict_src

    def yield_instances_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_reservations in self.execute(
                self.get_session_client(region=region).describe_instances, "Reservations", filters_req=filters_req
        ):
            for dict_src in dict_reservations["Instances"]:
                yield dict_src

    def get_all_instances(self, region=None):
        """
        Get all ec2 instances in current region.
        :return:
        """

        return list(self.yield_instances(region=region))

    def get_region_instances(self, region, filters=None, update_info=False):
        """
        Standard

        @param region:
        @param filters:
        @return:
        :param update_info:
        """

        return list(self.yield_instances(region=region, filters_req=filters, update_info=update_info))

    def yield_security_groups(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all volumes.

        :return:
        """

        regional_fetcher_generator = self.yield_security_groups_raw
        for dict_src in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  EC2SecurityGroup,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield dict_src

    def yield_security_groups_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_security_groups, "SecurityGroups", filters_req=filters_req
        ):
            yield dict_src

    def get_all_security_groups(self):
        """
        Get all security groups in the region.
        :return:
        """

        return list(self.yield_security_groups())

    def get_region_security_groups(self, region, filters=None):
        """
        Standard.

        @param region:
        @param filters:
        @return:
        """

        return list(self.yield_security_groups(region=region, filters_req=filters))

    def update_security_group_information(self, security_group):
        """
        Update security group information.

        @param security_group:
        @return:
        """

        filters = {"Filters": [
            {
                "Name": "group-name",
                "Values": [
                    security_group.name,
                ],
            }
        ]}

        if security_group.vpc_id is not None:
            filters["Filters"].append({"Name": "vpc-id", "Values": [security_group.vpc_id]})

        security_groups = self.get_region_security_groups(
            security_group.region, filters=filters
        )
        if len(security_groups) > 1:
            raise ValueError(
                f"Found {len(security_groups)} > 1 security groups by filters {filters}"
            )
        if len(security_groups) == 0:
            return False

        security_group.update_from_raw_response(security_groups[0].dict_src)
        return True

    def provision_security_group(self, desired_security_group, provision_rules=True):
        """
        Create/modify security group.
        todo:
        Generate permit_any_any on the outbound.
        add_request, revoke_request = security_group_region.generate_modify_ip_permissions_egress_requests(

        @param desired_security_group:
        @param provision_rules:
        @return:
        """

        existing_security_group = EC2SecurityGroup({})
        existing_security_group.name = desired_security_group.name
        existing_security_group.vpc_id = desired_security_group.vpc_id
        existing_security_group.region = desired_security_group.region

        if not self.update_security_group_information(existing_security_group):
            group_id = self.provision_security_group_raw(
                desired_security_group.generate_create_request()
            )
            existing_security_group.id = group_id

        desired_security_group.id = existing_security_group.id

        if not provision_rules:
            return

        (
            add_request,
            revoke_request,
            update_description,
        ) = existing_security_group.generate_modify_ip_permissions_requests(
            desired_security_group
        )

        if add_request:
            self.authorize_security_group_ingress_raw(add_request)

        if revoke_request:
            self.revoke_security_group_ingress_raw(revoke_request)

        if update_description:
            self.update_security_group_rule_descriptions_ingress_raw(update_description)

        self.update_security_group_information(desired_security_group)

    def provision_security_group_raw(self, request_dict, region=None):
        """
        Self explanatory.

        @param request_dict:
        @return:
        :param region:
        """

        logger.info(f"Creating security group {request_dict}")
        for group_id in self.execute(
                self.get_session_client(region=region).create_security_group, "GroupId", filters_req=request_dict
        ):
            return group_id

    def raw_create_security_group(self, request_dict, region=None):
        """
        Old style function.
        To remove!

        @param request_dict:
        @return:
        :param region:
        """

        logger.info(f"Creating security group {request_dict}")
        for group_id in self.execute(
                self.get_session_client(region=region).create_security_group, "GroupId", filters_req=request_dict
        ):
            return group_id

    def authorize_security_group_ingress(self, region, request_dict):
        """
        Old style. To remove!

        @param region:
        @param request_dict:
        @return:
        """
        AWSAccount.set_aws_region(region)
        try:
            return self.authorize_security_group_ingress_raw(request_dict)
        except Exception as inst_exception:
            if "The same permission must not appear multiple times" in repr(
                    inst_exception
            ):
                for request_ip_permission in request_dict["IpPermissions"]:
                    request_dict_tmp = {
                        "GroupId": request_dict["GroupId"],
                        "IpPermissions": [request_ip_permission],
                    }

                    self.authorize_security_group_ingress_raw(request_dict_tmp)
            else:
                raise

        return None

    def authorize_security_group_ingress_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        :param region:
        """
        logger.info(f"Authorizing security group ingress: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).authorize_security_group_ingress,
                "GroupId",
                filters_req=request_dict,
                raw_data=True,
        ):

            if "UnknownIpPermissions" in response:
                raise NotImplementedError(response)

            return response

    def revoke_security_group_ingress_raw(self, request_dict, region=None):
        """
        Revoke permission

        @param request_dict:
        @return:
        :param region:
        """

        logger.info(f"Revoking security group ingress: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).revoke_security_group_ingress,
                "GroupId",
                filters_req=request_dict,
                raw_data=True,
        ):

            if "unknownIpPermissionSet" in response:
                raise RuntimeError(response)

            return response

    def update_security_group_rule_descriptions_ingress_raw(self, request_dict, region=None):
        """
        Update description.

        @param request_dict:
        @return:
        :param region:
        """

        logger.info(f"Updating security group description ingress: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).update_security_group_rule_descriptions_ingress,
                "GroupId",
                filters_req=request_dict,
                raw_data=True,
        ):
            return response

    def create_instance(self, request_dict, region=None):
        """
        Raw create instance request.

        @param request_dict:
        @return:
        :param region:
        """

        for response in self.execute(
                self.get_session_client(region=region).run_instances, "Instances", filters_req=request_dict
        ):
            return response

    def create_key_pair(self, request_dict, region=None):
        """
        Raw create key_pair request.

        @param request_dict:
        @return:
        :param region:
        """

        for response in self.execute(
                self.get_session_client(region=region).create_key_pair, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def request_spot_fleet_raw(self, request_dict, region=None):
        """
        Raw request spot fleet request.

        @param request_dict:
        @return:
        :param region:
        """

        for response in self.execute(
                self.get_session_client(region=region).request_spot_fleet,
                "SpotFleetRequestId",
                filters_req=request_dict,
        ):
            return response

    def get_all_spot_fleet_requests(self, full_information=False):
        """
        Standard.

        @param full_information:
        @return:
        """

        final_result = []

        for _region in AWSAccount.get_aws_account().regions.values():
            region_results = self.get_region_spot_fleet_requests(_region, full_information=full_information)
            final_result += region_results

        return final_result

    def get_region_spot_fleet_requests(self, region, full_information=False):
        """
        Standard.

        :param full_information:
        :param region:
        :return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []

        for ret in self.execute(
                self.get_session_client(region=region).describe_spot_fleet_requests, "SpotFleetRequestConfigs"
        ):
            obj = EC2SpotFleetRequest(ret)
            if full_information is True:
                raise NotImplementedError()

            final_result.append(obj)

        return final_result

    def cancel_spot_fleet_requests_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """
        for response in self.execute(
                self.get_session_client(region=region).cancel_spot_fleet_requests, None, raw_data=True, filters_req=request
        ):
            return response

    def get_all_ec2_launch_templates(self, full_information=False, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """

        final_result = []

        if region is not None:
            return self.get_region_launch_templates(
                region, full_information=full_information
            )

        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_launch_templates(
                _region, full_information=full_information
            )

        return final_result

    def get_region_launch_templates(
            self, region, full_information=False, custom_filters=None
    ):
        """
        Standard

        @param region:
        @param full_information:
        @param custom_filters:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []
        logger.info(f"Fetching all launch templates from {region}")
        for ret in self.execute(
                self.get_session_client(region=region).describe_launch_templates,
                "LaunchTemplates",
                filters_req=custom_filters,
        ):
            obj = EC2LaunchTemplate(ret)
            obj.region = region
            if full_information is True:
                raise NotImplementedError()

            final_result.append(obj)
        return final_result

    def get_all_launch_template_versions(self, region=None):
        """
        Get all launch_template_versions in all regions.
        :return:
        """
        if region is not None:
            return self.get_region_launch_template_versions(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_launch_template_versions(_region)

        return final_result

    def get_region_launch_template_versions(self, region, custom_filters=None):
        """
        Standard

        @param region:
        @param custom_filters:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []

        def _callback_not_found_exception(exception_inst):
            return "NotFoundException" in repr(exception_inst)

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_launch_template_versions,
                "LaunchTemplateVersions",
                filters_req=custom_filters,
                exception_ignore_callback=_callback_not_found_exception,
        ):
            obj = EC2LaunchTemplateVersion(dict_src)
            final_result.append(obj)
        return final_result

    def raw_create_managed_prefix_list(self, request, add_client_token=False, region=None):
        """
        Standard

        @param request:
        @param add_client_token:
        @return:
        :param region:
        """

        if add_client_token:
            if "ClientToken" not in request:
                request["ClientToken"] = request["PrefixListName"]

        for response in self.execute(
                self.get_session_client(region=region).create_managed_prefix_list, "PrefixList", filters_req=request
        ):
            return response

    def raw_modify_managed_prefix_list(self, request, region=None):
        """
        Standard

        @param request:
        @return:
        :param region:
        """

        logger.info(f"Modifying prefix list with request: {request}")
        try:
            for response in self.execute(
                    self.get_session_client(region=region).modify_managed_prefix_list,
                    "PrefixList",
                    filters_req=request,
            ):
                return response
        except Exception as exception_instance:
            if "already exists" not in repr(exception_instance):
                raise

            logger.info(repr(exception_instance))

        return None

    def raw_describe_managed_prefix_list(
            self, region, pl_id=None, prefix_list_name=None
    ):
        """
        Standard

        @param region:
        @param pl_id:
        @param prefix_list_name:
        @return:
        """

        AWSAccount.set_aws_region(region)
        if pl_id is None and prefix_list_name is None:
            raise ValueError("pl_id pr prefix_list_name must be specified")

        request = {}
        if pl_id is not None:
            request["PrefixListIds"] = [pl_id]

        if prefix_list_name is not None:
            request["Filters"] = [
                {"Name": "prefix-list-name", "Values": [prefix_list_name]}
            ]

        for response in self.execute(
                self.get_session_client(region=region).describe_managed_prefix_lists,
                "PrefixLists",
                filters_req=request,
        ):
            return response

    def get_managed_prefix_list(
            self, region, pl_id=None, name=None, full_information=True
    ):
        """
        Standard

        @param region:
        @param pl_id:
        @param name:
        @param full_information:
        @return:
        """

        response = self.raw_describe_managed_prefix_list(
            region, pl_id=pl_id, prefix_list_name=name
        )
        if response is None:
            return None
        obj = ManagedPrefixList(response)
        if full_information:
            self.update_managed_prefix_list_full_information(obj)
        return obj

    def update_managed_prefix_list_full_information(self, prefix_list, region=None):
        """
        Standard

        @param prefix_list:
        @return:
        :param region:
        """

        def _ignore_unsupported_operation_callback(exception_instance):
            """
            Callback for ignoring exception.

            @param exception_instance:
            @return:
            """
            exception_message = repr(exception_instance)
            if (
                    "UnsupportedOperation" in exception_message
                    and "AWS-managed prefix list" in exception_message
            ):
                return True
            return False

        filters_req = {"PrefixListId": prefix_list.id}
        for associations_response in self.execute(
                self.get_session_client(region=region).get_managed_prefix_list_associations,
                "PrefixListAssociations",
                filters_req=filters_req,
                exception_ignore_callback=_ignore_unsupported_operation_callback,
        ):
            prefix_list.add_association_from_raw_response(associations_response)

        for entries_response in self.execute(
                self.get_session_client(region=region).get_managed_prefix_list_entries,
                "Entries",
                filters_req=filters_req,
        ):
            prefix_list.add_entry_from_raw_response(entries_response)

    def get_all_managed_prefix_lists(self, full_information=True, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """

        if region is not None:
            return self.get_region_managed_prefix_lists(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_managed_prefix_lists(
                _region, full_information=full_information
            )
        return final_result

    def get_region_managed_prefix_lists(
            self, region, full_information=True, custom_filters=None
    ):
        """
        Standard

        @param custom_filters:
        @param region:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []

        for response in self.execute(
                self.get_session_client(region=region).describe_managed_prefix_lists,
                "PrefixLists",
                filters_req=custom_filters,
        ):
            obj = ManagedPrefixList(response)
            if full_information is True:
                self.update_managed_prefix_list_full_information(obj)

            final_result.append(obj)

        return final_result

    def provision_vpc(self, vpc):
        """
        Standard

        @param vpc:
        @return:
        """

        lst_vpcs = self.get_all_vpcs(region=vpc.region)
        for vpc_exists in lst_vpcs:
            if vpc_exists.get_tagname(ignore_missing_tag=True) == vpc.get_tagname():
                if vpc_exists.cidr_block != vpc.cidr_block:
                    raise RuntimeError(
                        f"VPC {vpc_exists.name} exists with different cidr_block {vpc_exists.cidr_block} != {vpc.cidr_block}"
                    )
                vpc.id = vpc_exists.id
                for request in vpc_exists.generate_modify_vpc_attribute_requests(desired=vpc):
                    self.modify_vpc_attribute_raw(request)
                return

        if vpc.id is None:
            response = self.provision_vpc_raw(vpc.generate_create_request())
            vpc.update_from_raw_create(response)

            for request in vpc.generate_modify_vpc_attribute_requests():
                self.modify_vpc_attribute_raw(request)

    def provision_vpc_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """
        for response in self.execute(
                self.get_session_client(region=region).create_vpc, "Vpc", filters_req=request
        ):
            self.clear_cache(VPC)
            return response

    def modify_vpc_attribute_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """
        logger.info(f"Modifying VPC {request}")
        for response in self.execute(
                self.get_session_client(region=region).modify_vpc_attribute, None, filters_req=request, raw_data=True
        ):
            self.clear_cache(VPC)
            return response

    def provision_subnets(self, subnets):
        """
        Standard.

        @param subnets:
        @return:
        """

        for subnet in subnets[1:]:
            if subnet.region.region_mark != subnets[0].region.region_mark:
                raise RuntimeError("All subnets should be in one region")

        region_subnets = self.get_region_subnets(subnets[0].region)
        for subnet in subnets:
            for region_subnet in region_subnets:
                if (
                        region_subnet.get_tagname(ignore_missing_tag=True)
                        == subnet.get_tagname()
                ):
                    if region_subnet.cidr_block != subnet.cidr_block:
                        raise RuntimeError(
                            f"Subnet {subnet.get_tagname()} exists with different cidr_block {region_subnet.cidr_block} != {subnet.cidr_block}"
                        )
                    subnet.update_from_raw_create(region_subnet.dict_src)

        for subnet in subnets:
            if subnet.id is not None:
                continue
            try:
                response = self.provision_subnet_raw(subnet.generate_create_request())
                subnet.id = response["SubnetId"]
            except Exception as exception_inst:
                if "conflicts with another subnet" in repr(exception_inst):
                    logger.warning(
                        f"{subnet.generate_create_request()}: {repr(exception_inst)}"
                    )
                    continue
                raise

    def dispose_subnets(self, subnets):
        """
        Standard.

        @param subnets:
        @return:
        """
        for subnet in subnets[1:]:
            if subnet.region.region_mark != subnets[0].region.region_mark:
                raise RuntimeError("All subnets should be in one region")

        region_subnets = self.get_region_subnets(subnets[0].region)
        for subnet in subnets:
            for region_subnet in region_subnets:
                if (
                        region_subnet.get_tagname(ignore_missing_tag=True)
                        == subnet.get_tagname()
                ):
                    if region_subnet.cidr_block != subnet.cidr_block:
                        raise RuntimeError(
                            f"Subnet {subnet.get_tagname()} exists with different cidr_block {region_subnet.cidr_block} != {subnet.cidr_block}"
                        )
                    subnet.update_from_raw_create(region_subnet.dict_src)

        for subnet in subnets:
            if subnet.id is None:
                raise RuntimeError(f"Subnet ID is None for subnet {subnet.get_tagname()}")

            self.delete_subnet_raw({"SubnetId": subnet.id})

    def delete_subnet_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """

        logger.info(f"Deleting subnet {request}")

        for response in self.execute(
                self.get_session_client(region=region).delete_subnet, None, raw_data=True, filters_req=request
        ):
            self.clear_cache(Subnet)
            return response

        return None

    def dispose_route_tables(self, route_tables):
        """
        Standard.

        @param route_tables:
        @return:
        """

        if len(route_tables) == 0:
            return True

        AWSAccount.set_aws_region(route_tables[0].region)

        for route_table in route_tables[1:]:
            if route_table.region.region_mark != route_tables[0].region.region_mark:
                raise RuntimeError("All route_tables should be in one region")

        region_route_tables = self.get_region_route_tables(route_tables[0].region)
        for route_table in route_tables:
            for region_route_table in region_route_tables:
                if (
                        region_route_table.get_tagname(ignore_missing_tag=True)
                        == route_table.get_tagname()
                ):
                    if region_route_table.vpc_id != route_table.vpc_id:
                        raise RuntimeError(
                            f"Subnet {route_table.get_tagname()} exists with different vpc_id {region_route_table.vpc_id} != {route_table.vpc_id}"
                        )
                    route_table.update_from_raw_response(region_route_table.dict_src)

        for route_table in route_tables:
            if route_table.id is None:
                raise RuntimeError(f"Route_table ID is None for route_table {route_table.get_tagname()}")

            self.delete_route_table_raw({"RouteTableId": route_table.id})

        return True

    def delete_route_table_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """

        logger.info(f"Deleting route table {request}")

        for response in self.execute(
                self.get_session_client(region=region).delete_route_table, None, raw_data=True, filters_req=request
        ):
            self.clear_cache(RouteTable)
            return response

        return None

    def dispose_security_groups(self, security_groups):
        """
        Standard.

        @param security_groups:
        @return:
        """

        if len(security_groups) == 0:
            return True

        for security_group in security_groups[1:]:
            if security_group.region.region_mark != security_groups[0].region.region_mark:
                raise RuntimeError("All security_groups should be in one region")

        region_security_groups = self.get_region_security_groups(security_groups[0].region)
        for security_group in security_groups:
            for region_security_group in region_security_groups:
                if (
                        region_security_group.get_tagname(ignore_missing_tag=True)
                        == security_group.get_tagname()
                ):
                    security_group.id = region_security_group.id

        for security_group in security_groups:
            if security_group.id is None:
                raise RuntimeError(f"security_group ID is None for security_group {security_group.get_tagname()}")

            self.delete_security_group_raw({"GroupId": security_group.id})
        return True

    def delete_security_group_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """

        logger.info(f"Deleting security_group {request}")

        for response in self.execute(
                self.get_session_client(region=region).delete_security_group, None, raw_data=True, filters_req=request
        ):
            self.clear_cache(EC2SecurityGroup)
            return response

        return None

    def provision_subnet_raw(self, request, region=None):
        """
        Standard.

        @param request:
        @return:
        :param region:
        """

        for response in self.execute(
                self.get_session_client(region=region).create_subnet, "Subnet", filters_req=request
        ):
            self.clear_cache(Subnet)
            return response

        return None

    def provision_managed_prefix_list(self, managed_prefix_list, declarative=False):
        """
        Provisioning managed prefix list.

        @param managed_prefix_list:
        @param declarative:
        @return:
        """

        logger.info(
            f"Manged prefix list '{managed_prefix_list.name}' in region '{managed_prefix_list.region.region_mark}'"
        )
        raw_region_pl = self.raw_describe_managed_prefix_list(
            managed_prefix_list.region, prefix_list_name=managed_prefix_list.name
        )

        if raw_region_pl is None:
            AWSAccount.set_aws_region(managed_prefix_list.region)
            response = self.raw_create_managed_prefix_list(
                managed_prefix_list.generate_create_request()
            )
            self.clear_cache(ManagedPrefixList)
            return managed_prefix_list.update_from_raw_create(response)

        region_object = ManagedPrefixList(raw_region_pl)
        self.update_managed_prefix_list_full_information(region_object)

        request = region_object.get_entries_modify_request(
            managed_prefix_list, declarative
        )
        if request is not None:
            self.raw_modify_managed_prefix_list(request)
            raw_region_pl = self.raw_describe_managed_prefix_list(
                managed_prefix_list.region, prefix_list_name=managed_prefix_list.name
            )
            self.clear_cache(ManagedPrefixList)

        managed_prefix_list.update_from_raw_create(raw_region_pl)
        return None

    def yield_amis(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all amis.

        :return:
        """

        regional_fetcher_generator = self.yield_amis_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  AMI,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield obj

    def yield_amis_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_images, "Images", filters_req=filters_req
        ):
            yield dict_src

    def get_all_amis(self, region=None):
        """
        Self explanatory.

        @param region:
        @return:
        """

        return list(self.yield_amis(region=region))

    def get_region_amis(self, region, custom_filters=None):
        """
        Standard.

        @param region:
        @param custom_filters:
        @return:
        """

        return list(self.yield_amis(region=region, filters_req=custom_filters))

    def create_image(self, instance: EC2Instance, timeout=600):
        """
        Create ec2 image from an instance.

        @param instance:
        @param timeout:
        @return:
        """

        # snapshots_raw = self.create_snapshots(instance)
        AWSAccount.set_aws_region(instance.region)
        ami_id = self.create_image_raw(instance.generate_create_image_request())
        filter_request = {"ImageIds": [ami_id]}

        amis = self.get_region_amis(instance.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(filter_request)
        new_ami = amis[0]

        logger.info(f"Starting waiting loop for ami to become ready: {new_ami.id}")

        self.wait_for_status(
            new_ami,
            self.update_image_information,
            [new_ami.State.AVAILABLE],
            [new_ami.State.PENDING],
            [
                new_ami.State.INVALID,
                new_ami.State.DEREGISTERED,
                new_ami.State.TRANSIENT,
                new_ami.State.FAILED,
                new_ami.State.ERROR,
            ],
            timeout=timeout,
        )
        return new_ami

    def create_image_raw(self, request_dict, region=None):
        """
        Create image from dict request.

        @param request_dict:
        @return:
        :param region:
        """

        for response in self.execute(
                self.get_session_client(region=region).create_image, "ImageId", filters_req=request_dict
        ):
            return response

    def create_snapshots(self, instance):
        """
        Create a snapshot of the instacne.

        @param instance:
        @return:
        """

        start = datetime.datetime.now()
        AWSAccount.set_aws_region(instance.region)
        ret = self.create_snapshots_raw(instance.generate_create_snapshots_request())
        end = datetime.datetime.now()
        logger.info(f"Snapshot creation took {end - start}")
        return ret

    def create_snapshots_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        :param region:
        """
        return list(
            self.execute(
                self.get_session_client(region=region).create_snapshots, "Snapshots", filters_req=request_dict
            )
        )

    def get_all_key_pairs(self, full_information=True, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """
        if region is not None:
            return self.get_region_key_pairs(region, full_information=full_information)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_key_pairs(
                _region, full_information=full_information
            )
        return final_result

    def get_region_key_pairs(self, region, full_information=True):
        """
        Standard

        @param region:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []

        for response in self.execute(self.get_session_client(region=region).describe_key_pairs, "KeyPairs"):
            obj = KeyPair(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def get_all_internet_gateways(self, full_information=True, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """
        if region is not None:
            return self.get_region_internet_gateways(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_internet_gateways(
                _region, full_information=full_information
            )
        return final_result

    def get_region_internet_gateways(
            self, region, full_information=True, custom_filters=None, filters_req=None
    ):
        """
        Standard

        @param custom_filters:
        @param filters_req:
        @param region:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []
        if custom_filters:
            raise DeprecationWarning("Use 'filters_req' instead")

        for response in self.execute(
                self.get_session_client(region=region).describe_internet_gateways,
                "InternetGateways",
                filters_req=filters_req,
        ):
            obj = InternetGateway(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def update_internet_gateway_information(self, internet_gateway: InternetGateway):
        """
        Standard.

        :param internet_gateway:
        :return:
        """

        region_objects = self.get_region_internet_gateways(internet_gateway.region, filters_req={"Filters": [{"Name": "tag:name", "Values": [internet_gateway.get_tagname()]}]})
        if len(region_objects) > 1:
            raise RuntimeError(f"Was not expected to find 1 region object. Found: {len(region_objects)}")
        if not region_objects:
            return False

        internet_gateway.update_from_raw_response(region_objects[0].dict_src)
        return True

    def get_all_vpc_peerings(self, full_information=True, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """
        if region is not None:
            return self.get_region_vpc_peerings(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_vpc_peerings(
                _region, full_information=full_information
            )
        return final_result

    def get_region_vpc_peerings(self, region, full_information=True):
        """
        Standard

        @param region:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []

        for response in self.execute(
                self.get_session_client(region=region).describe_vpc_peering_connections, "VpcPeeringConnections"
        ):
            obj = VPCPeering(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def yield_route_tables(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all route_tables.

        :return:
        """

        regional_fetcher_generator = self.yield_route_tables_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  RouteTable,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield certificate

    def yield_route_tables_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_route_tables, "RouteTables", filters_req=filters_req
        ):
            yield dict_src

    def get_all_route_tables(self, region=None):
        """
        Standard

        @param region:
        @return:
        """

        return list(self.yield_route_tables(region=region))

    def get_region_route_tables(self, region, update_info=False):
        """
        Standard

        @param region:
        @param update_info:
        @return:
        """

        return list(self.yield_route_tables(region=region, update_info=update_info))

    def get_all_elastic_addresses(self, full_information=True, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """
        if region is not None:
            return self.get_region_elastic_addresses(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_elastic_addresses(
                _region, full_information=full_information
            )
        return final_result

    def get_region_elastic_addresses(self, region, full_information=True):
        """
        Standard

        @param region:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []

        for response in self.execute(self.get_session_client(region=region).describe_addresses, "Addresses"):
            obj = ElasticAddress(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def get_all_nat_gateways(self, full_information=True, region=None):
        """
        Standard

        @param full_information:
        @param region:
        @return:
        """
        if region is not None:
            return self.get_region_nat_gateways(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_nat_gateways(
                _region, full_information=full_information
            )
        return final_result

    def get_region_nat_gateways(
            self,
            region,
            full_information=True,
            custom_filters=None,
    ):
        """
        Standard

        @param custom_filters:
        @param region:
        @param full_information:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []
        filters_req = None if custom_filters is None else {"Filters": custom_filters}

        for response in self.execute(
                self.get_session_client(region=region).describe_nat_gateways, "NatGateways", filters_req=filters_req
        ):
            obj = NatGateway(response)
            if full_information is True:
                pass

            final_result.append(obj)

        return final_result

    def provision_internet_gateway(self, internet_gateway):
        """
        Create and/or attach internet_gateway

        @param internet_gateway:
        @return:
        """
        region_gateways = self.get_region_internet_gateways(internet_gateway.region)
        for region_gateway in region_gateways:
            if (
                    region_gateway.get_tagname(ignore_missing_tag=True)
                    == internet_gateway.get_tagname()
            ):
                internet_gateway.id = region_gateway.id
                break

        if internet_gateway.id is None:
            try:
                response = self.provision_internet_gateway_raw(
                    internet_gateway.generate_create_request()
                )
                internet_gateway.id = response["InternetGatewayId"]
                region_gateway = InternetGateway(response)
            except Exception as exception_inst:
                logger.warning(
                    f"{internet_gateway.generate_create_request()}: {repr(exception_inst)}"
                )
                raise

        attachment_vpc_ids = [att["VpcId"] for att in internet_gateway.attachments]
        for vpc_id in attachment_vpc_ids:
            if vpc_id in [att["VpcId"] for att in region_gateway.attachments]:
                attachment_vpc_ids.remove(vpc_id)

        for attachment_vpc_id in attachment_vpc_ids:
            request = {
                "InternetGatewayId": internet_gateway.id,
                "VpcId": attachment_vpc_id,
            }
            self.attach_internet_gateway_raw(request)

    def provision_internet_gateway_raw(self, request, region=None):
        """
        Standard

        @param request:
        @return:
        :param region:
        """
        for response in self.execute(
                self.get_session_client(region=region).create_internet_gateway, "InternetGateway", filters_req=request
        ):
            self.clear_cache(InternetGateway)
            return response

    def dispose_internet_gateway(self, inet_gateway, force=True):
        """
        Standard

        @param inet_gateway:
        @return:
        :param force:
        """
        region = inet_gateway.region
        if region is None:
            raise ValueError("Region was not set")

        if inet_gateway.id is None:
            if not self.update_internet_gateway_information(inet_gateway):
                return True

        if inet_gateway.attachments:
            if force:
                for attachment in inet_gateway.attachments:
                    logger.info(f"Detaching internet gateway: {inet_gateway.id}, {attachment['VpcId']}")
                    for _ in self.execute(self.get_session_client(region=region).detach_internet_gateway, None, raw_data=True, filters_req={"InternetGatewayId": inet_gateway.id, "VpcId": attachment["VpcId"]}):
                        break
            else:
                raise RuntimeError(f"{inet_gateway.attachments=}")

        logger.info(f"Disposing internet gateway: {inet_gateway.id}")
        AWSAccount.set_aws_region(inet_gateway.region)
        for response in self.execute(
                self.get_session_client(region=region).delete_internet_gateway, None, raw_data=True, filters_req={"InternetGatewayId": inet_gateway.id}
        ):
            self.clear_cache(InternetGateway)
            return response

    def attach_internet_gateway_raw(self, request, region=None):
        """
        Standard

        @param request:
        @return:
        :param region:
        """
        logger.info(request)
        for response in self.execute(
                self.get_session_client(region=region).attach_internet_gateway, "ResponseMetadata", filters_req=request
        ):
            return response

    def provision_elastic_address(self, elastic_address):
        """
        Standard

        @param elastic_address:
        @return:
        """
        region_elastic_addresses = self.get_region_elastic_addresses(
            elastic_address.region
        )
        for region_elastic_address in region_elastic_addresses:
            if (
                    region_elastic_address.get_tagname(ignore_missing_tag=True)
                    == elastic_address.get_tagname()
            ):
                elastic_address.update_from_raw_response(
                    region_elastic_address.dict_src
                )
                return

        try:
            response = self.provision_elastic_address_raw(
                elastic_address.generate_create_request()
            )
            del response["ResponseMetadata"]
            elastic_address.update_from_raw_response(response)
        except Exception as exception_inst:
            repr_exception_inst = repr(exception_inst)
            logger.warning(repr_exception_inst)
            raise

    def provision_elastic_address_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        :param region:
        """
        for response in self.execute(
                self.get_session_client(region=region).allocate_address, "", filters_req=request_dict, raw_data=True
        ):
            return response

    def provision_vpc_peering(self, vpc_peering):
        """
        Request peering and accept on the other end.

        @param vpc_peering:
        @return:
        """
        region_vpc_peerings = self.get_region_vpc_peerings(vpc_peering.region)
        for region_vpc_peering in region_vpc_peerings:
            if region_vpc_peering.get_status() in [
                region_vpc_peering.Status.DELETED,
                region_vpc_peering.Status.DELETING,
            ]:
                continue
            if (
                    region_vpc_peering.get_tagname(ignore_missing_tag=True)
                    != vpc_peering.get_tagname()
            ):
                continue

            vpc_peering.update_from_raw_response(region_vpc_peering.dict_src)

            if region_vpc_peering.get_status() in [
                region_vpc_peering.Status.ACTIVE,
                region_vpc_peering.Status.PROVISIONING,
            ]:
                return
            break

        if vpc_peering.id is None:
            AWSAccount.set_aws_region(vpc_peering.region)
            response = self.provision_vpc_peering_raw(
                vpc_peering.generate_create_request()
            )
            vpc_peering.update_from_raw_response(response)

        if vpc_peering.get_status() in [
            vpc_peering.Status.INITIATING_REQUEST,
            vpc_peering.Status.PENDING_ACCEPTANCE,
        ]:
            AWSAccount.set_aws_region(vpc_peering.peer_region)
            for _ in range(20):
                try:
                    self.accept_vpc_peering_connection_raw(
                        vpc_peering.generate_accept_request()
                    )
                    break
                except Exception as exception_inst:
                    repr_exception_inst = repr(exception_inst)
                    if "does not exist" not in repr_exception_inst:
                        raise
                time.sleep(5)
        else:
            raise RuntimeError(vpc_peering.get_status())

    def provision_vpc_peering_raw(self, request_dict, region=None):
        """
        create_vpc_peering_connection

        @param request_dict:
        @return:
        """
        logger.info(f"Creating VPC Peering: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_vpc_peering_connection,
                "VpcPeeringConnection",
                filters_req=request_dict,
        ):
            return response

    def accept_vpc_peering_connection_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).accept_vpc_peering_connection,
                "VpcPeeringConnection",
                filters_req=request_dict,
        ):
            return response

    def find_launch_template(self, launch_template):
        """
        By name.

        @param launch_template:
        @return:
        """
        region_objects = self.get_region_launch_templates(
            launch_template.region,
            custom_filters={"LaunchTemplateNames": [launch_template.name]},
        )

        if len(region_objects) > 1:
            raise RuntimeError("len(region_objects) > 1")

        return region_objects[0] if region_objects else None

    def find_region_launch_template_version(self, launch_template):
        """
        Find the latest version.

        @param launch_template:
        @return:
        """
        region_objects = self.get_region_launch_template_versions(
            launch_template.region,
            custom_filters={
                "LaunchTemplateName": launch_template.name,
                "Versions": ["$Latest"],
            },
        )

        if len(region_objects) > 1:
            raise RuntimeError("len(region_objects) > 1")

        return region_objects[0] if region_objects else None

    def provision_launch_template(self, launch_template: EC2LaunchTemplate):
        """
        Standard

        @param launch_template:
        @return:
        """

        current_launch_template_version = self.find_region_launch_template_version(
            launch_template
        )
        if current_launch_template_version is not None:
            provision_version_request = (
                current_launch_template_version.generate_create_request(launch_template)
            )
            if provision_version_request:
                response = self.provision_launch_template_version_raw(
                    provision_version_request
                )
                current_launch_template_version.update_from_raw_response(response)
                request = launch_template.generate_modify_launch_template_request(
                    str(current_launch_template_version.version_number)
                )
                response = self.modify_launch_template_raw(request)
                launch_template.update_from_raw_response(response)
            else:
                region_object = self.find_launch_template(launch_template)
                launch_template.update_from_raw_response(region_object.dict_src)
            return

        response = self.provision_launch_template_raw(
            launch_template.generate_create_request()
        )

        launch_template.update_from_raw_response(response)

    def provision_launch_template_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Creating Launch Template: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_launch_template,
                "LaunchTemplate",
                filters_req=request_dict,
        ):
            return response

    def provision_launch_template_version_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Creating Launch Template Version: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_launch_template_version,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            if "Warning" in str(response):
                raise RuntimeError(response)
            return response["LaunchTemplateVersion"]

    def modify_launch_template_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Modifying Launch Template Version: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).modify_launch_template,
                "LaunchTemplate",
                filters_req=request_dict,
        ):
            return response

    def provision_nat_gateway(self, nat_gateway):
        """
        Standard

        @param nat_gateway:
        @return:
        """
        region_gateways = self.get_region_nat_gateways(nat_gateway.region)
        for region_gateway in region_gateways:
            if region_gateway.get_state() not in [
                region_gateway.State.AVAILABLE,
                region_gateway.State.PENDING,
            ]:
                continue
            if (
                    region_gateway.get_tagname(ignore_missing_tag=True)
                    == nat_gateway.get_tagname()
            ):
                nat_gateway.update_from_raw_response(region_gateway.dict_src)
                return

        try:
            response = self.provision_nat_gateway_raw(
                nat_gateway.generate_create_request()
            )
            nat_gateway.update_from_raw_response(response)
        except Exception as exception_inst:
            logger.warning(repr(exception_inst))
            raise

    def provision_nat_gateway_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).create_nat_gateway, "NatGateway", filters_req=request_dict
        ):
            return response

    def dispose_nat_gateway(self, nat_gateway, dry_run=False):
        """
        Standard

        @param nat_gateway:
        @param dry_run:
        @return:
        """

        return self.dispose_nat_gateway_raw(nat_gateway.generate_dispose_request(dry_run=dry_run))

    def dispose_nat_gateway_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).delete_nat_gateway, "NatGatewayId", filters_req=request_dict
        ):
            return response

    def provision_route_table(self, route_table: RouteTable):
        """
        Standard

        @param route_table:
        @return:
        """

        AWSAccount.set_aws_region(route_table.region)

        region_route_tables = self.get_region_route_tables(route_table.region)
        for region_route_table in region_route_tables:
            if route_table.id is not None:
                if route_table.id == region_route_table.id:
                    break
            elif (
                    region_route_table.get_tagname(ignore_missing_tag=True)
                    == route_table.get_tagname()
            ):
                break
        else:
            response = self.provision_route_table_raw(
                route_table.generate_create_request()
            )
            region_route_table = RouteTable(response)
            self.clear_cache(RouteTable)
        create_tags_request, delete_tags_request = self.generate_tags_requests(region_route_table, route_table)
        if create_tags_request:
            self.clear_cache(RouteTable)
            self.create_tags_raw(create_tags_request)
        if delete_tags_request:
            self.clear_cache(RouteTable)
            self.delete_tags_raw(delete_tags_request)

        request = region_route_table.generate_associate_route_table_request(route_table)
        if request:
            self.associate_route_table_raw(request)

        create_requests, replace_requests = region_route_table.generate_change_route_requests(route_table)
        for create_request in create_requests:
            self.create_route_raw(create_request)
        for replace_request in replace_requests:
            self.replace_route_raw(replace_request)

    def generate_tags_requests(self, current_object, desired_object):
        """
        Create, modify or delete tags.

        :param current_object:
        :param desired_object:
        :return:
        """

        to_del = []
        to_create = []
        for tag in current_object.tags:
            if tag not in desired_object.tags:
                to_del.append(tag)

        for tag in desired_object.tags:
            if tag not in current_object.tags:
                to_create.append(tag)
        create_request = None if not to_create else {"Resources": [current_object.id], "Tags": to_create}
        delete_request = None if not to_del else {"Resources": [current_object.id], "Tags": to_del}
        return create_request, delete_request

    def add_routes(self, route_table):
        """
        Create route table routes.

        @param route_table:
        @return:
        """

        region_route_tables = self.get_region_route_tables(route_table.region)
        for region_route_table in region_route_tables:
            if (
                    region_route_table.get_tagname(ignore_missing_tag=True)
                    == route_table.get_tagname()
            ):
                break
        else:
            raise RuntimeError(f"Can not find route table: {route_table.get_tagname()}")

        AWSAccount.set_aws_region(route_table.region)
        requests, _ = region_route_table.generate_change_route_requests(route_table, declarative=False)
        for request in requests:
            self.create_route_raw(request)

    def provision_route_table_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).create_route_table, "RouteTable", filters_req=request_dict
        ):
            return response

    def associate_route_table_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Associating route table: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).associate_route_table, "AssociationId", filters_req=request_dict
        ):
            return response

    def create_route_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Creating route {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_route, "Return", filters_req=request_dict, instant_raise=True,
        ):
            self.clear_cache(RouteTable)
            return response

    def replace_route_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        logger.info(f"Replacing route {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).replace_route, None, filters_req=request_dict, raw_data=True
        ):
            self.clear_cache(RouteTable)
            return response

    def get_region_ec2_instances(self, region, custom_filters=None):
        """
        Standard

        @param custom_filters:
        @param region:
        @return:
        """
        AWSAccount.set_aws_region(region)
        final_result = []
        for instance in self.execute(
                self.get_session_client(region=region).describe_instances, "Reservations", filters_req=custom_filters
        ):
            final_result.extend(instance["Instances"])
        return [EC2Instance(instance) for instance in final_result]

    def provision_ec2_instance(
            self, ec2_instance: EC2Instance, wait_until_active=False, tagname_uid=True,
    ):
        """
        Standard

        @param ec2_instance:
        @param wait_until_active:
        @return:
        :param tagname_uid:
        """

        if tagname_uid:
            filter_by_tag = {
                "Filters": [{"Name": "tag:Name", "Values": [ec2_instance.get_tagname()]}]
            }
            region_ec2_instances = self.get_region_ec2_instances(
                ec2_instance.region, custom_filters=filter_by_tag
            )
            for region_ec2_instance in region_ec2_instances:
                if region_ec2_instance.get_state() not in [
                    region_ec2_instance.State.RUNNING,
                    region_ec2_instance.State.PENDING,
                ]:
                    continue

                if (
                        region_ec2_instance.get_tagname(ignore_missing_tag=True)
                        == ec2_instance.get_tagname()
                ):
                    ec2_instance.update_from_raw_response(region_ec2_instance.dict_src)
                    return

                raise RuntimeError("Filter by tag Name did not work.")

        try:
            response = self.provision_ec2_instance_raw(
                ec2_instance.generate_create_request()
            )
            ec2_instance.update_from_raw_response(response)
        except Exception as exception_inst:
            logger.warning(repr(exception_inst))
            raise

        if wait_until_active:
            try:
                self.wait_for_status(
                    ec2_instance,
                    self.update_instance_information,
                    [ec2_instance.State.RUNNING],
                    [ec2_instance.State.PENDING],
                    [
                        ec2_instance.State.SHUTTING_DOWN,
                        ec2_instance.State.TERMINATED,
                        ec2_instance.State.STOPPING,
                        ec2_instance.State.STOPPED,
                    ],
                )
            except Exception as error_instance:
                logger.error(repr(error_instance))
                time.sleep(30)
                self.wait_for_status(
                    ec2_instance,
                    self.update_instance_information,
                    [ec2_instance.State.RUNNING],
                    [ec2_instance.State.PENDING],
                    [
                        ec2_instance.State.SHUTTING_DOWN,
                        ec2_instance.State.TERMINATED,
                        ec2_instance.State.STOPPING,
                        ec2_instance.State.STOPPED,
                    ],
                )

    def update_instance_information(self, instance: EC2Instance):
        """
        Standard

        @param instance:
        @return:
        """
        filters = {"Filters": [{"Name": "instance-id", "Values": [instance.id]}]}
        instance_new = self.get_region_instances(instance.region, filters=filters)[0]
        instance.update_from_raw_response(instance_new.dict_src)

    def update_image_information(self, ami: AMI):
        """
        Standard

        @param ami:
        @return:
        """
        filter_request = {"ImageIds": [ami.id]}
        amis = self.get_region_amis(ami.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(filter_request)

        ami_new = amis[0]

        ami.update_from_raw_response(ami_new.dict_src)

    def provision_ec2_instance_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).run_instances, "Instances", filters_req=request_dict
        ):
            return response

    def provision_key_pair(self, key_pair: KeyPair):
        """
        Standard

        @param key_pair:
        @return:
        """
        region_key_pairs = self.get_region_key_pairs(key_pair.region)
        for region_key_pair in region_key_pairs:
            if region_key_pair.name == key_pair.name:
                key_pair.id = region_key_pair.id
                return None

        response = self.provision_key_pair_raw(key_pair.generate_create_request())
        key_pair.update_from_raw_response(response)
        return response

    def provision_key_pair_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Provisioning key_pair: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_key_pair, None, filters_req=request_dict, raw_data=True
        ):
            return response

    def associate_elastic_address_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).associate_address, None, filters_req=request_dict, raw_data=True
        ):
            return response

    @staticmethod
    def generate_user_data_from_file(file_path):
        """
        Standard

        @param file_path:
        @return:
        """
        with open(file_path, encoding="utf-8") as file_handler:
            user_data = file_handler.read()
        return base64.b64encode(user_data.encode()).decode("ascii")

    def dispose_launch_template(self, launch_template):
        """
        Standard

        @param launch_template:
        @return:
        """

        AWSAccount.set_aws_region(launch_template.region)
        self.dispose_launch_template_raw(launch_template.generate_dispose_request())

    def dispose_launch_template_raw(self, request_dict, region=None):
        """
        Standard

        @param request_dict:
        @return:
        """

        for response in self.execute(
                self.get_session_client(region=region).delete_launch_template,
                "LaunchTemplate",
                filters_req=request_dict,
                exception_ignore_callback=lambda x: "NotFoundException" in repr(x),
        ):
            return response

    def dispose_instance(self, instance: EC2Instance, dry_run=False):
        """
        Standard

        @param instance:
        @param dry_run:
        @return:
        """

        AWSAccount.set_aws_region(instance.region)
        self.dispose_instance_raw(instance.generate_dispose_request(dry_run=dry_run))

    def dispose_instance_raw(self, request_dict, region=None):
        """
        Standard.

        @param request_dict:
        @return:
        """
        for response in self.execute(
                self.get_session_client(region=region).terminate_instances,
                "TerminatingInstances",
                filters_req=request_dict,
        ):
            return response

    def stop_instance(self, ec2_instance):
        """
        Stop the instance. Wait for stopped state.

        :param ec2_instance:
        :return:
        """

        if ec2_instance.region is None:
            raise ValueError("Region ws not set")

        list(self.execute(self.get_session_client(region=ec2_instance.region).stop_instances, "StoppingInstances",
                          filters_req={"InstanceIds": [ec2_instance.id], "Force": True}))

        self.wait_for_status(
            ec2_instance,
            self.update_instance_information,
            [ec2_instance.State.STOPPED],
            [ec2_instance.State.RUNNING,
             ec2_instance.State.PENDING,
             ec2_instance.State.SHUTTING_DOWN,
             ec2_instance.State.STOPPING],
            [
                ec2_instance.State.TERMINATED
            ],
        )

    def update_volume_information(self, volume):
        """
        Update current status.

        :param volume:
        :return:
        """

        AWSAccount.set_aws_region(volume.region)

        if volume.id is not None:
            filters_req = {"Filters": [{"Name": "volume-id", "Values": [volume.id]}]}
        else:
            filters_req = {"Filters": [{"Name": "tag:Name", "Values": [volume.get_tagname()]}]}

        lst_ret = list(self.yield_volumes(region=volume.region, filters_req=filters_req))

        if len(lst_ret) > 1:
            raise RuntimeError(f"Found more then 1 ec2 volume with filter: {filters_req}")

        if len(lst_ret) == 1:
            volume.update_from_raw_response(lst_ret[0].dict_src)
            return

        if volume.id:
            raise RuntimeError(f"Didn't find volume by id: {filters_req}")

    def update_modification_information(self, modification):
        """
        Update modification from AWS

        :param modification:
        :return:
        """
        ret = self.get_region_volume_modifications(modification.region, filters_req={"Filters": [
            {
                "Name": "volume-id",
                "Values": [
                    modification.volume_id,
                ]
            },
        ]})

        if len(ret) == 0:
            return False
        if len(ret) > 1:
            raise ValueError(f"found more then a single modification for volume id: {modification.volume_id}")

        modification.update_from_raw_response(ret[0].dict_src)
        return True

    def provision_volume(self, desired_volume):
        """
        Standard.

        :param desired_volume:
        :return:
        """
        current_volume = EC2Volume({})
        current_volume.id = desired_volume.id
        current_volume.tags = desired_volume.tags
        current_volume.region = desired_volume.region
        self.update_volume_information(current_volume)

        if current_volume.id is None:
            response = self.create_volume_raw(desired_volume.generate_create_request())
            desired_volume.update_from_raw_response(response)
            self.wait_for_status(
                desired_volume,
                self.update_volume_information,
                [desired_volume.State.AVAILABLE, desired_volume.State.IN_USE],
                [desired_volume.State.CREATING, desired_volume.State.DELETING],
                [
                    desired_volume.State.DELETED,
                    desired_volume.State.ERROR,
                ]
            )
            current_volume = desired_volume

        if current_volume.get_state() == current_volume.State.CREATING:
            self.wait_for_status(
                current_volume,
                self.update_volume_information,
                [current_volume.State.AVAILABLE, current_volume.State.IN_USE],
                [current_volume.State.CREATING],
                [
                    current_volume.State.DELETED,
                    current_volume.State.ERROR,
                ]
            )
        elif current_volume.get_state() not in [current_volume.State.AVAILABLE, current_volume.State.IN_USE]:
            raise ValueError(f"Volume '{current_volume.id}' is in {current_volume.get_state()} state")
        request = current_volume.generate_modify_request(desired_volume)
        if request is not None:
            response = self.modify_volume_raw(request)
            modification = EC2VolumeModification(response)
            modification.region = current_volume.region
            modification.volume_id = current_volume.id
            self.wait_for_status(modification, self.update_modification_information, [modification.State.COMPLETED],
                                 [modification.State.OPTIMIZING, modification.State.MODIFYING],
                                 [modification.State.FAILED], timeout=30*60)

        self.update_volume_information(desired_volume)

    def create_volume_raw(self, dict_request, region=None):
        """
        Standard.

        :param dict_request:
        :return:
        """

        for response in self.execute(self.get_session_client(region=region).create_volume, None, raw_data=True,
                                     filters_req=dict_request):
            del response["ResponseMetadata"]
            self.clear_cache(EC2Volume)
            return response

    def modify_volume_raw(self, dict_request, region=None):
        """
        Standard.

        :param dict_request:
        :return:
        """
        for response in self.execute(self.get_session_client(region=region).modify_volume, "VolumeModification",
                                     filters_req=dict_request, instant_raise=True):
            self.clear_cache(EC2Volume)
            return response

    def dispose_volume(self, volume):
        """
        Dispose EC2 volume.

        :param volume:
        :return:
        """

        if volume.region is None:
            raise ValueError("Region was not set")

        self.update_volume_information(volume)
        if volume.id is None:
            return None

        for response in self.execute(self.get_session_client(region=volume.region).delete_volume, None, raw_data=True,
                                     filters_req={"VolumeId": volume.id}):
            self.clear_cache(volume.__class__)
            return response

    def dispose_vpc(self, vpc):
        """
        Dispose EC2 volume.

        :param vpc:
        :return:
        """

        lst_vpcs = self.get_all_vpcs(region=vpc.region)
        for vpc_exists in lst_vpcs:
            if vpc_exists.get_tagname(ignore_missing_tag=True) == vpc.get_tagname():
                if vpc_exists.cidr_block != vpc.cidr_block:
                    raise RuntimeError(
                        f"Disposing VPC {vpc_exists.name} exists with different cidr_block {vpc_exists.cidr_block} != {vpc.cidr_block}"
                    )
                request = {"VpcId": vpc_exists.id}
                break
        else:
            return True

        for response in self.execute(self.get_session_client(region=vpc.region).delete_vpc, None, raw_data=True,
                                     filters_req=request):
            self.clear_cache(VPC)
            return response

    def attach_volume(self, volume, device_name, instance_id):
        """
        Attach if not attached.

        :return:
        """

        if volume.region is None:
            raise ValueError("Region was not set")

        if volume.id is None:
            self.update_volume_information(volume)

        for attachment in volume.attachments:
            current_attachment_instance_id = attachment["InstanceId"]
            if current_attachment_instance_id == instance_id:
                current_attachment_device_name = attachment["Device"]
                if current_attachment_device_name == device_name:
                    return True

                raise RuntimeError(f"Volume must be attached to {instance_id}: {device_name}, but attached to"
                                   f" {current_attachment_instance_id}: {current_attachment_device_name}")

        dict_req = {
            "Device": device_name,
            "InstanceId": instance_id,
            "VolumeId": volume.id
        }

        return self.attach_volume_raw(dict_req)

    def attach_volume_raw(self, dict_req, region=None):
        """
        Device='string',
        InstanceId='string',
        VolumeId='string',
        DryRun=True|False

        :return:
        """

        for response in self.execute(self.get_session_client(region=region).attach_volume, None, raw_data=True, filters_req=dict_req):
            return response

    def get_instance_password(self, instance, private_key_file_path):
        """
        Return instance autogenerated password.

        :param private_key_file_path:
        :param instance:
        :return:
        """

        # pylint: disable= import-outside-toplevel
        from Crypto.Cipher import PKCS1_v1_5
        # pylint: disable= import-outside-toplevel
        from Crypto.PublicKey import RSA
        AWSAccount.set_aws_region(instance.region)

        with open(private_key_file_path, "r", encoding="utf-8") as key_file:
            key_text = key_file.read()
        key = RSA.importKey(key_text)
        cipher = PKCS1_v1_5.new(key)

        dict_req = {"InstanceId": instance.id}
        for response in self.execute(self.get_session_client(region=instance.region).get_password_data, "PasswordData", filters_req=dict_req):
            return cipher.decrypt(base64.b64decode(response), None).decode('utf8')

    def get_region_instance_types(self, region):
        """
        Standard.

        :param region:
        :return:
        """

        return list(self.yield_instance_types(region=region))

    def yield_instance_types(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all instance_types.

        :return:
        """

        regional_fetcher_generator = self.yield_instance_types_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  EC2InstanceType,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield certificate

    def yield_instance_types_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_instance_types, "InstanceTypes", filters_req=filters_req
        ):
            yield dict_src

    def yield_volumes(self, region=None, update_info=False, filters_req=None):
        """
        Yield over all volumes.

        :return:
        """

        regional_fetcher_generator = self.yield_volumes_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  EC2Volume,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                                    filters_req=filters_req):
            yield certificate

    def yield_volumes_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_volumes, "Volumes", filters_req=filters_req
        ):
            yield dict_src

    def get_all_volumes(self, region=None, update_info=False, filters_req=None):
        """
        Get all ec2 volumes in current region.

        :return:
        """

        return list(self.yield_volumes(region=region, update_info=update_info, filters_req=filters_req))

    def get_region_volume_modifications(self, region, filters_req=None):
        """
        Standard

        @param region:
        @param filters_req:
        @return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_volumes_modifications, "VolumesModifications", filters_req=filters_req
        ):
            final_result.append(EC2VolumeModification(dict_src))

        return final_result

    def modify_instance_attribute_raw(self, request, region=None):
        """
        modify_instance_attribute request.

        :return:
        """

        logger.info(f"Modifying instance: {request}")
        for response in self.execute(
                self.get_session_client(region=region).modify_instance_attribute, None, raw_data=True, filters_req=request
        ):
            self.clear_cache(EC2Instance)
            return response

    def start_instances_raw(self, request, region=None):
        """
        modify_instance_attribute request.

        :return:
        """

        logger.info(f"Starting instances: {request}")
        for response in self.execute(
                self.get_session_client(region=region).start_instances, "StartingInstances", filters_req=request
        ):
            return response

    def create_tags_raw(self, request, region=None):
        """
        Creates or modifies tags.

        :return:
        """

        logger.info(f"Creating or modifying tags: {request}")
        for response in self.execute(
                self.get_session_client(region=region).create_tags, None, raw_data=True, filters_req=request
        ):
            return response

    def delete_tags_raw(self, request, region=None):
        """
        Deletes tags.

        :return:
        """

        logger.info(f"Deleting tags: {request}")
        for response in self.execute(
                self.get_session_client(region=region).delete_tags, None, raw_data=True, filters_req=request
        ):
            return response

    def yield_regions(self, update_info=False, filters_req=None):
        """
        Yield over all regions.

        :return:
        """

        regional_fetcher_generator = self.yield_regions_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  Region,
                                                  update_info=update_info,
                                                  filters_req=filters_req,
                                                            global_service=True):
            try:
                delattr(obj, "region")
            except AttributeError:
                pass
            yield obj

    def yield_regions_raw(self, filters_req=None, region=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_regions, "Regions", filters_req=filters_req
        ):
            yield dict_src
