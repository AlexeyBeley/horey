"""
AWS iam client to handle iam service API requests.
"""

from horey.aws_api.aws_services_entities.iam_user import IamUser
from horey.aws_api.aws_services_entities.iam_access_key import IamAccessKey
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_group import IamGroup
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile

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

    # pylint: disable= too-many-arguments
    def yield_users(self, update_info=False, filters_req=None, full_information=True):
        """
        Yield users

        :return:
        """

        regional_fetcher_generator = self.yield_users_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            IamUser,
                                                            update_info=update_info,
                                                            full_information_callback=self.update_user_information if full_information else None,
                                                            global_service=True,
                                                            filters_req=filters_req)

    def yield_users_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).list_users, "Users", filters_req=filters_req
        )

    def get_all_users(self, full_information=True):
        """
        Get all users

        :param full_information:
        :return:
        """

        return list(self.yield_users(full_information=full_information))

    def get_all_users_old(self, full_information=True):
        """
        Get all users.

        :param full_information:
        :return:
        """

        final_result = []

        for response in self.execute(self.get_session_client().list_users, "Users"):
            user = IamUser(response)
            final_result.append(user)
            if full_information:
                self.update_user_information(user, full_information=True)

        return final_result

    def update_user_information(self, user: IamUser, full_information=True):
        """
        Get current information from AWS.

        :param user:
        :param full_information:
        :return:
        """

        for response in self.execute(
                self.get_session_client().get_user,
                "User",
                filters_req={"UserName": user.name}, exception_ignore_callback=lambda x: "NoSuchEntity" in repr(x)
        ):
            user.update_from_raw_response(response)
            break
        else:
            return False

        if full_information:
            policies = list(
                self.execute(
                    self.get_session_client().list_user_policies,
                    "PolicyNames",
                    filters_req={"UserName": user.name},
                )
            )

            user.policies = [
                list(
                    self.execute(
                        self.get_session_client().get_user_policy,
                        "PolicyDocument",
                        filters_req={
                            "UserName": user.name,
                            "PolicyName": policy_name,
                        },
                    )
                )[0]
                for policy_name in policies
            ]

            user.attached_policies = list(
                self.execute(
                    self.get_session_client().list_attached_user_policies,
                    "AttachedPolicies",
                    filters_req={"UserName": user.name},
                )
            )

            user.groups = list(
                self.execute(
                    self.get_session_client().list_groups_for_user,
                    "Groups",
                    filters_req={"UserName": user.name},
                )
            )

        return True

    def get_account_authorization_details(self):
        """
        Account's security details.

        @return:
        """

        ret = []
        for update_info in self.execute(
                self.get_session_client().get_account_authorization_details, None, raw_data=True
        ):
            ret.append(update_info)
        return ret

    def get_all_access_keys(self):
        """
        Get all access keys.

        :return:
        """

        final_result = []
        users = self.get_all_users()

        for user in users:
            for result in self.execute(
                    self.get_session_client().list_access_keys,
                    "AccessKeyMetadata",
                    filters_req={"UserName": user.name},
            ):
                final_result.append(IamAccessKey(result))

        return final_result

    # pylint: disable= too-many-arguments
    def yield_roles(self, update_info=False, filters_req=None, full_information=True):
        """
        Yield roles

        :return:
        """

        regional_fetcher_generator = self.yield_roles_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            IamRole,
                                                            update_info=update_info,
                                                            full_information_callback=self.get_role_full_information if full_information else None,
                                                            global_service=True,
                                                            filters_req=filters_req)

    def yield_roles_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).list_roles, "Roles", filters_req=filters_req
        )

    def get_all_roles(self, full_information=True):
        """
        Get all roles

        :param full_information:
        :return:
        """

        return list(self.yield_roles(full_information=full_information))

    # pylint: disable= too-many-arguments
    def yield_groups(self, update_info=False, filters_req=None, full_information=True):
        """
        Yield groups

        :return:
        """

        regional_fetcher_generator = self.yield_groups_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            IamGroup,
                                                            update_info=update_info,
                                                            full_information_callback=self.update_group_full_information if full_information else None,
                                                            global_service=True,
                                                            filters_req=filters_req)

    def yield_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).list_groups, "Groups", filters_req=filters_req
        )

    def get_all_groups(self, full_information=True):
        """
        Get all groups

        :param full_information:
        :return:
        """

        return list(self.yield_groups(full_information=full_information))

    def update_group_full_information(self, group):
        """
        * Fetch inline policies' names for the group.
        * Fetch attached policies.

        @param group:
        @return:
        """

        policy_names = list(
            self.execute(
                self.get_session_client().list_group_policies,
                "PolicyNames",
                filters_req={"GroupName": group.name},
            )
        )
        group.policies = []
        for policy_name in policy_names:
            for response in self.execute(
                    self.get_session_client().get_group_policy,
                    None,
                    raw_data=True,
                    filters_req={"GroupName": group.name, "PolicyName": policy_name},
            ):
                del response["ResponseMetadata"]
                group.policies.append(response)

        group.attached_policies = list(
            self.execute(
                self.get_session_client().list_attached_group_policies,
                "AttachedPolicies",
                filters_req={"GroupName": group.name},
            )
        )

    def get_all_instance_profiles(self):
        """
        Get all instance profiles.

        @return:
        """

        final_result = []
        for result in self.execute(
                self.get_session_client().list_instance_profiles,
                "InstanceProfiles"
        ):
            instance_profile = IamInstanceProfile(result)
            final_result.append(instance_profile)
        return final_result

    def get_role_full_information(self, iam_role):
        """

        :param iam_role:
        :return:
        """

        if self.update_role_information(iam_role):
            self.update_role_managed_policies(iam_role)
            self.update_role_inline_policies(iam_role)
            return True

        return False

    def update_role_information(self, iam_role: IamRole, full_information=True):
        """
        Full information part update.

        :param iam_role:
        :param full_information:
        :return:
        """

        for response in self.execute(
                self.get_session_client().get_role, "Role", filters_req={"RoleName": iam_role.name},
                exception_ignore_callback=lambda x: "NoSuchEntityException" in repr(x)
        ):
            iam_role.update_from_raw_response(response)
            if full_information:
                self.update_role_managed_policies(iam_role)
                self.update_role_inline_policies(iam_role)
            return True
        return False

    def update_role_managed_policies(self, iam_role):
        """
        Full information part

        @param iam_role:
        @return:
        """

        iam_role.managed_policies_arns = [dict_src["PolicyArn"] for dict_src in self.execute(
            self.get_session_client().list_attached_role_policies,
            "AttachedPolicies",
            filters_req={"RoleName": iam_role.name},
        )]

    def update_role_inline_policies(self, iam_role: IamRole):
        """
        Full information part update - inline policies

        :param iam_role:
        :return:
        """

        policies = []
        for policy_name in self.execute(
                self.get_session_client().list_role_policies,
                "PolicyNames",
                filters_req={"RoleName": iam_role.name, "MaxItems": 1000},
        ):
            for document in self.execute(
                    self.get_session_client().get_role_policy,
                    "PolicyDocument",
                    filters_req={"RoleName": iam_role.name, "PolicyName": policy_name},
            ):
                policy_dict = {"PolicyName": policy_name,
                               "Document": document
                               }
                policy = IamPolicy(policy_dict)
                policies.append(policy)

        iam_role.inline_policies = policies

    # pylint: disable= too-many-arguments
    def yield_policies(self, update_info=False, filters_req=None, full_information=True):
        """
        Yield policies

        :return:
        """

        regional_fetcher_generator = self.yield_policies_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            IamPolicy,
                                                            update_info=update_info,
                                                            full_information_callback=self.update_policy_default_statement if full_information else None,
                                                            global_service=True,
                                                            filters_req=filters_req)

    def yield_policies_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).list_policies, "Policies", filters_req=filters_req
        )

    def get_all_policies(self, full_information=True, filters_req=None):
        """
        Get all iam policies.

        @param full_information:
        @param filters_req:
        @return:
        """

        return list(self.yield_policies(full_information=full_information, filters_req=filters_req))

    def update_policy_default_statement(self, policy: IamPolicy):
        """
        Fetches and updates the policy statements

        :param policy: The IamPolicy obj
        :return: None, raise if fails
        """

        for response in self.execute(
                self.get_session_client().get_policy_version,
                "PolicyVersion",
                filters_req={
                    "PolicyArn": policy.arn,
                    "VersionId": policy.default_version_id,
                },
        ):
            policy.update_from_raw_response(response)

    def update_policy_versions(self, policy: IamPolicy):
        """
        Fetches and updates the policy documents' versions

        :param policy: The IamPolicy obj
        :return: None, raise if fails
        """

        policy.versions = list(self.execute(
            self.get_session_client().list_policy_versions,
            "Versions",
            filters_req={
                "PolicyArn": policy.arn
            },
        ))

    def attach_role_policy_raw(self, request_dict):
        """
        Attach a policy to role.

        @param request_dict:
        @return:
        """

        logger.info(f"Attaching policy to role: {request_dict}")
        for response in self.execute(
                self.get_session_client().attach_role_policy,
                None,
                filters_req=request_dict,
                raw_data=True,
        ):
            self.clear_cache(IamRole)
            return response

    def detach_role_policy_raw(self, request_dict):
        """
        Detach a policy from role.

        @param request_dict:
        @return:
        """

        logger.info(f"Detaching policy from role: {request_dict}")
        for response in self.execute(
                self.get_session_client().detach_role_policy,
                None,
                filters_req=request_dict,
                raw_data=True,
        ):
            self.clear_cache(IamRole)
            return response

    def attach_role_inline_policy(self, role: IamRole, policy: IamPolicy):
        """
        Attach a policy to role.

        @param role:
        @param policy:
        @return:
        """

        logger.info(f"Attaching policy {policy.name} to role: {role.name}")
        request_dict = {"RoleName": role.name,
                        "PolicyName": policy.name,
                        "PolicyDocument": policy.document}

        return self.put_role_policy_raw(request_dict=request_dict)

    def put_role_policy_raw(self, request_dict):
        """
        Attach an inline policy to role.

        @param request_dict:
        @return:
        """

        logger.info(f"Putting inline role policy: {request_dict}")

        for response in self.execute(
                self.get_session_client().put_role_policy, "ResponseMetadata", filters_req=request_dict
        ):
            self.clear_cache(IamRole)
            return response

    def delete_role_policy_raw(self, request_dict):
        """
        Delete an inline policy to role.

        @param request_dict:
        @return:
        """

        logger.info(f"Deleting inline role policy: {request_dict}")

        for response in self.execute(
                self.get_session_client().delete_role_policy, "ResponseMetadata", filters_req=request_dict
        ):
            self.clear_cache(IamRole)
            return response

    def provision_role(self, iam_role: IamRole):
        """
        Provision role object

        @param iam_role:
        @return:
        """

        region_role = IamRole({})
        region_role.name = iam_role.name
        region_role.path = iam_role.path
        if not self.get_role_full_information(region_role):
            role_dict_src = self.provision_iam_role_raw(
                iam_role.generate_create_request()
            )
            region_role.update_from_raw_response(role_dict_src)

        attach_requests, detach_requests = region_role.generate_managed_policies_requests(iam_role)
        for attach_request in attach_requests:
            self.attach_role_policy_raw(attach_request)
        for detach_request in detach_requests:
            self.detach_role_policy_raw(detach_request)

        put_requests, delete_requests = region_role.generate_inline_policies_requests(iam_role)
        for put_request in put_requests:
            self.put_role_policy_raw(put_request)

        for delete_request in delete_requests:
            self.delete_role_policy_raw(delete_request)

        update_assume_role_policy_request = region_role.generate_update_assume_role_policy_request(iam_role)
        if update_assume_role_policy_request:
            self.update_assume_role_policy_raw(update_assume_role_policy_request)

        self.update_role_information(iam_role)

    def dispose_role(self, role: IamRole, detach_policies=False):
        """
        Standard.

        :param detach_policies:
        :param role:
        :return:
        """

        if not self.update_role_information(role):
            return True

        if detach_policies:
            self.detach_role_policies(role)

        logger.warning(f"Deleting iam role: {role.name}")

        for response in self.execute(
                self.get_session_client().delete_role, None, filters_req={"RoleName": role.name}, raw_data=True,
                exception_ignore_callback=lambda x: "NoSuchEntity" in repr(x)
        ):
            self.clear_cache(IamRole)
            return response

    def detach_role_policies(self, role):
        """
        Detach policies from the role.

        :param role:
        :return:
        """

        for policy_arn in role.managed_policies_arns:
            request = {"RoleName": role.name, "PolicyArn": policy_arn}
            logger.warning(f"Detaching policy from role: {request}")

            for response in self.execute(
                    self.get_session_client().detach_role_policy, None, raw_data=True, filters_req=request
            ):
                return response
            self.clear_cache(IamRole)

    def provision_iam_role_raw(self, request_dict):
        """
        Provision iam role from raw request dict.

        @param request_dict:
        @return:
        """

        logger.warning(f"Creating iam role: {request_dict}")

        for response in self.execute(
                self.get_session_client().create_role, "Role", filters_req=request_dict
        ):
            self.clear_cache(IamRole)
            return response

    def update_instance_profile_information(
            self, iam_instance_profile: IamInstanceProfile
    ):
        """
        Fetch and update instance profile info.

        @param iam_instance_profile:
        @return:
        """

        for response in self.execute(
                self.get_session_client().get_instance_profile,
                "InstanceProfile",
                filters_req={"InstanceProfileName": iam_instance_profile.name},
                exception_ignore_callback=lambda x: "NoSuchEntity" in repr(x),
        ):
            iam_instance_profile.update_from_raw_response(response)
            return True
        return False

    def provision_instance_profile(self, iam_instance_profile: IamInstanceProfile):
        """
        Provision instance profile object.

        @param iam_instance_profile:
        @return:
        """

        current_iam_instance_profile = IamInstanceProfile({})
        current_iam_instance_profile.name = iam_instance_profile.name
        if not self.update_instance_profile_information(current_iam_instance_profile):
            self.provision_iam_instance_profile_raw(
                iam_instance_profile.generate_create_request()
            )
            for request in iam_instance_profile.generate_add_role_requests():
                self.add_role_to_instance_profile_raw(request)

        self.update_instance_profile_information(iam_instance_profile)

    def update_assume_role_policy_raw(self, request):
        """

        :return:
        """

        logger.info(f"Updating role assume policy {request}")

        for response in self.execute(
                self.get_session_client().update_assume_role_policy,
                None,
                raw_data=True,
                filters_req=request,
        ):
            return response

    def add_role_to_instance_profile_raw(self, request):
        """
        Add role to existing instance profile.

        @param request:
        @return:
        """

        logger.info(f"add_role_to_instance_profile: {request}")
        for response in self.execute(
                self.get_session_client().add_role_to_instance_profile,
                None,
                raw_data=True,
                filters_req=request,
        ):
            return response

    def provision_iam_instance_profile_raw(self, request_dict):
        """
        Provision instance profile role from raw dict.

        @param request_dict:
        @return:
        """

        logger.warning(f"create_instance_profile: {request_dict}")

        for response in self.execute(
                self.get_session_client().create_instance_profile,
                "InstanceProfile",
                filters_req=request_dict,
        ):
            return response

    def update_policy_information(self, policy, full_information=False):
        """
        Update policy data.

        :param policy:
        :param full_information:
        :return:
        """

        request_dict = {"PolicyArn": policy.arn}
        try:
            for response in self.execute(
                    self.get_session_client().get_policy,
                    "Policy",
                    filters_req=request_dict,
                    instant_raise=True
            ):

                policy.update_from_raw_response(response)
                if full_information:
                    self.update_policy_default_statement(policy)
                    self.update_policy_versions(policy)

                return True
        except Exception as error_instance:
            if "NoSuchEntity" in repr(error_instance):
                return False
            raise

    def provision_policy(self, policy_desired: IamPolicy):
        """
        Provision policy from object.

        @param policy_desired:
        @return:
        """

        existing_policy = IamPolicy({})
        existing_policy.path = policy_desired.path
        existing_policy.arn = policy_desired.generate_arn(self.account_id)
        if not self.update_policy_information(existing_policy, full_information=True):
            for existing_policy in self.yield_policies(full_information=False):
                if existing_policy.name == policy_desired.name:
                    if existing_policy.path != policy_desired.path:
                        raise ValueError(
                            f"Existing policy path: '{existing_policy.path}' when desired is {policy_desired.path}")
                    break
            else:
                dict_src = self.provision_policy_raw(policy_desired.generate_create_request())
                policy_desired.update_from_raw_response(dict_src)
                return

        create_version_request = existing_policy.generate_create_policy_version_request(policy_desired)
        if create_version_request is None:
            policy_desired.arn = existing_policy.arn
            self.update_policy_information(policy_desired, full_information=True)
            return

        delete_version_request = existing_policy.generate_delete_policy_version_request()
        if delete_version_request is not None:
            for _ in self.execute(
                    self.get_session_client().delete_policy_version, None, raw_data=True,
                    filters_req=delete_version_request
            ):
                break

        logger.info(f"Pushing new policy version: {create_version_request}")
        for _ in self.execute(
                self.get_session_client().create_policy_version, "PolicyVersion", filters_req=create_version_request
        ):
            policy_desired.arn = existing_policy.arn
            self.update_policy_information(policy_desired, full_information=True)

    def provision_policy_raw(self, request_dict):
        """
        Provision policy from raw dict.

        @param request_dict:
        @return:
        """

        logger.warning(f"Creating iam policy: {request_dict}")
        for response in self.execute(
                self.get_session_client().create_policy, "Policy", filters_req=request_dict
        ):
            self.clear_cache(IamPolicy)
            return response

    def provision_user(self, user_desired: IamUser):
        """
        Provision user from object.

        @param user_desired:
        @return:
        """
        existing_user = IamUser({})
        existing_user.name = user_desired.name
        self.update_user_information(existing_user, full_information=True)
        if existing_user.id is not None:
            logger.info(f"Updating user: {user_desired.name}")

        self.provision_user_raw(user_desired.generate_create_request())
        self.update_user_information(user_desired)

    def provision_user_raw(self, request_dict):
        """
        Provision user from raw dict.

        @param request_dict:
        @return:
        """
        logger.warning(f"Creating iam user: {request_dict}")

        for response in self.execute(
                self.get_session_client().create_user, "User", filters_req=request_dict
        ):
            return response

    def dispose_user(self, user):
        """
        Delete user.

        :param user:
        :return:
        """

        logger.warning(f"Disposing iam user: {user.name}")

        for response in self.execute(
                self.get_session_client().delete_user, None, raw_data=True, filters_req={"UserName": user.name}
        ):
            return response

    def create_access_key(self, user):
        """
        Request new user access key.

        :param user:
        :return:
        """
        request = {"UserName": user.name}
        return self.create_access_key_raw(request)

    def create_access_key_raw(self, request_dict):
        """
        Create user access key.

        @param request_dict:
        @return:
        """

        logger.info(f"Creating iam user access key: {request_dict}")

        for response in self.execute(
                self.get_session_client().create_access_key, "AccessKey", filters_req=request_dict
        ):
            return response

    def delete_access_key_raw(self, request_dict):
        """
        Delete user access key.
        response = client.delete_access_key(
            UserName='string',
            AccessKeyId='string'
        )

        @param request_dict:
        @return:
        """

        logger.warning(f"Deleting iam user access key: {request_dict}")

        for response in self.execute(
                self.get_session_client().delete_access_key, None, raw_data=True, filters_req=request_dict
        ):
            return response
