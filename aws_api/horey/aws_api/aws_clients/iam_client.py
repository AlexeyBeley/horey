"""
AWS iam client to handle iam service API requests.
"""
import pdb

from horey.aws_api.aws_services_entities.iam_user import IamUser
from horey.aws_api.aws_services_entities.iam_access_key import IamAccessKey
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_group import IamGroup
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.common_utils.common_utils import CommonUtils

from horey.h_logger import get_logger

logger = get_logger()


class IamClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "Marker"
    NEXT_PAGE_INITIAL_KEY = ""

    def __init__(self):
        client_name = "iam"
        super().__init__(client_name)

    def get_all_users(self, full_information=True):
        """
        Get all users.

        :param full_information:
        :return:
        """

        final_result = []

        for response in self.execute(self.client.list_users, "Users"):
            user = IamUser(response)
            final_result.append(user)
            if full_information:
                user.policies = list(self.execute(self.client.list_user_policies,
                                                           "PolicyNames",
                                                           filters_req={"UserName": user.name}))

                user.attached_policies = list(self.execute(self.client.list_attached_user_policies,
                                                           "AttachedPolicies",
                                                           filters_req={"UserName": user.name}))

                user.groups = list(self.execute(self.client.list_groups_for_user,
                                                           "Groups",
                                                           filters_req={"UserName": user.name}))

        if full_information:
            for update_info in self.execute(self.client.get_account_authorization_details, "UserDetailList"):
                _user = CommonUtils.find_objects_by_values(final_result, {"id": update_info["UserId"]}, max_count=1)[0]
                _user.update_attributes(update_info)

        return final_result

    def get_all_access_keys(self):
        """
        Get all access keys.

        :return:
        """

        final_result = []
        users = self.get_all_users()

        for user in users:
            for result in self.execute(self.client.list_access_keys, "AccessKeyMetadata", filters_req={"UserName": user.name}):
                final_result.append(IamAccessKey(result))

        return final_result

    def get_all_roles(self, full_information=True, policies=None):
        """
        Get all roles

        :param full_information:
        :param policies:
        :return:
        """

        final_result = []
        for result in self.execute(self.client.list_roles, "Roles", filters_req={"MaxItems": 1000}):
            role = IamRole(result)
            final_result.append(role)
            if full_information:
                self.update_iam_role_full_information(role, policies=policies)

        return final_result
    
    def get_all_groups(self, full_information=True):
        """
        Get all groups

        :param full_information:
        :param policies:
        :return:
        """

        final_result = []
        for result in self.execute(self.client.list_groups, "Groups", filters_req={"MaxItems": 1000}):
            group = IamGroup(result)
            final_result.append(group)
            if full_information:
                self.update_group_full_information(group)

        return final_result

    def update_group_full_information(self, group):
        """
        * Fetch inline policies' names for the group.
        * Fetch attached policies.

        @param group:
        @return:
        """

        group.policies = list(self.execute(self.client.list_group_policies, "PolicyNames", filters_req={"MaxItems": 1000, "GroupName": group.name}))
        group.attached_policies = list(self.execute(self.client.list_attached_group_policies, "AttachedPolicies", filters_req={"MaxItems": 1000, "GroupName": group.name}))

    def get_all_instance_profiles(self):
        """
        Get all instance profiles.

        @return:
        """

        final_result = []
        for result in self.execute(self.client.list_instance_profiles, "InstanceProfiles", filters_req={"MaxItems": 1000}):
            instance_profile = IamInstanceProfile(result)
            final_result.append(instance_profile)
        return final_result

    def update_iam_role_full_information(self, iam_role, policies=None):
        """

        :param iam_role:
        :param policies: if policies already polled, you can pass them to save time.
        :return:
        """

        self.update_role_information(iam_role)

        if policies is None:
            policies = self.get_all_policies(full_information=False, filters_req={"OnlyAttached": True})

        self.update_iam_role_managed_policies(iam_role, policies=policies)
        self.update_iam_role_inline_policies(iam_role)

    def update_role_information(self, iam_role):
        """
        Full information part update.
        :param iam_role:
        :return:
        """
        ret = self.execute(self.client.get_role, "Role", filters_req={"RoleName": iam_role.name})
        update_info = next(ret)
        iam_role.update_extended(update_info)

    def update_iam_role_managed_policies(self, iam_role, policies=None):
        """
        Full information part

        @param iam_role:
        @param policies:
        @return:
        """
        if policies is None:
            return

        for managed_policy in self.execute(self.client.list_attached_role_policies, "AttachedPolicies", filters_req={"RoleName": iam_role.name, "MaxItems": 1000}):
            found_policies = CommonUtils.find_objects_by_values(policies, {"arn": managed_policy["PolicyArn"]})

            if len(found_policies) != 1:
                found_policies = [managed_policy["PolicyArn"]]

            policy = found_policies[0]
            iam_role.add_policy(policy)

    def update_iam_role_inline_policies(self, iam_role):
        """
        Full information part update.
        :param iam_role:
        :return:
        """
        for poilcy_name in self.execute(self.client.list_role_policies, "PolicyNames", filters_req={"RoleName": iam_role.name, "MaxItems": 1000}):
            for document_dict in self.execute(self.client.get_role_policy, "PolicyDocument", filters_req={"RoleName": iam_role.name, "PolicyName": poilcy_name}):
                policy_dict = {"PolicyName": poilcy_name}
                policy = IamPolicy(policy_dict)

                policy_dict = {"Document": document_dict}
                policy.update_statements(policy_dict)

                iam_role.add_policy(policy)

    def yield_policies(self, full_information=True, filters_req=None):
        """
        Yield all policies objects.

        @param full_information:
        @param filters_req:
        @return:
        """

        for result in self.execute(self.client.list_policies, "Policies", filters_req=filters_req):
            pol = IamPolicy(result)
            if full_information:
                self.update_policy_default_statement(pol)
            yield pol

    def get_all_policies(self, full_information=True, filters_req=None):
        """
        Get all iam policies.

        @param full_information:
        @param filters_req:
        @return:
        """

        final_result = []

        for result in self.execute(self.client.list_policies, "Policies", filters_req=filters_req):
            pol = IamPolicy(result)
            if full_information:
                self.update_policy_default_statement(pol)
            final_result.append(pol)

        return final_result

    def update_policy_default_statement(self, policy):
        """
        Fetches and updates the policy statements

        :param policy: The IamPolicy obj
        :return: None, raise if fails
        """

        for response in self.execute(self.client.get_policy_version, "PolicyVersion", filters_req={"PolicyArn": policy.arn, "VersionId": policy.default_version_id}):
            policy.update_statements(response)

    def attach_role_policy_raw(self, request_dict):
        """
        Attach a policy to role.

        @param request_dict:
        @return:
        """

        logger.info(f"Attaching policy to role: {request_dict}")
        for response in self.execute(self.client.attach_role_policy, "Role", filters_req=request_dict, raw_data=True):
            return response

    def attach_role_inline_policy_raw(self, request_dict):
        """
        Attach an inline policy to role.

        @param request_dict:
        @return:
        """

        for response in self.execute(self.client.put_role_policy, "ResponseMetadata", filters_req=request_dict):
            return response

    def provision_iam_role(self, iam_role: IamRole):
        """
        Provision role object

        @param iam_role:
        @return:
        """

        all_roles = self.get_all_roles(full_information=False)
        found_role = CommonUtils.find_objects_by_values(all_roles, {"name": iam_role.name})

        if found_role:
            found_role = found_role[0]
            role_dict_src = found_role.dict_src
        else:
            role_dict_src = self.provision_iam_role_raw(iam_role.generate_create_request())

        iam_role.update_from_raw_response(role_dict_src)

        for request in iam_role.generate_attach_policies_requests():
            self.attach_role_policy_raw(request)

    def provision_iam_role_raw(self, request_dict):
        """
        Provision iam role from raw request dict.

        @param request_dict:
        @return:
        """

        logger.warning(f"Creating iam role: {request_dict}")

        for response in self.execute(self.client.create_role, "Role", filters_req=request_dict):
            return response

    def update_instance_profile_information(self, iam_instance_profile: IamInstanceProfile):
        """
        Fetch and update instance profile info.

        @param iam_instance_profile:
        @return:
        """

        for response in self.execute(self.client.get_instance_profile, "InstanceProfile", filters_req={"InstanceProfileName": iam_instance_profile.name},
                                     exception_ignore_callback=lambda x: "NoSuchEntity" in repr(x)):
            iam_instance_profile.update_from_raw_response(response)

    def provision_instance_profile(self, iam_instance_profile: IamInstanceProfile):
        """
        Provision instance profile object.

        @param iam_instance_profile:
        @return:
        """

        all_instance_profiles = self.get_all_instance_profiles()
        found_profiles = CommonUtils.find_objects_by_values(all_instance_profiles, {"name": iam_instance_profile.name})

        if len(found_profiles) > 2:
            raise RuntimeError(f"More then 1 profiles found by name: {iam_instance_profile.name}")

        if len(found_profiles) == 0:
            self.provision_iam_instance_profile_raw(iam_instance_profile.generate_create_request())
            for request in iam_instance_profile.generate_add_role_requests():
                self.add_role_to_instance_profile_raw(request)

        self.update_instance_profile_information(iam_instance_profile)

    def add_role_to_instance_profile_raw(self, request):
        """
        Add role to existing instance profile.

        @param request:
        @return:
        """

        logger.info(f"add_role_to_instance_profile: {request}")
        for response in self.execute(self.client.add_role_to_instance_profile, None, raw_data=True, filters_req=request):
            return response

    def provision_iam_instance_profile_raw(self, request_dict):
        """
        Provision instance profile role from raw dict.

        @param request_dict:
        @return:
        """

        logger.warning(f"create_instance_profile: {request_dict}")

        for response in self.execute(self.client.create_instance_profile, "InstanceProfile", filters_req=request_dict):
            return response

    def provision_policy(self, policy: IamPolicy):
        """
        Provision policy from object.

        @param policy:
        @return:
        """

        for existing_policy in self.yield_policies(full_information=False):
            if existing_policy.name == policy.name:
                policy.update_from_raw_response(existing_policy.dict_src)
                return

        role_dict_src = self.provision_policy_raw(policy.generate_create_request())
        policy.update_from_raw_response(role_dict_src)

    def provision_policy_raw(self, request_dict):
        """
        Provision policy from raw dict.

        @param request_dict:
        @return:
        """

        logger.warning(f"Creating iam policy: {request_dict}")

        for response in self.execute(self.client.create_policy, "Policy", filters_req=request_dict):
            return response
