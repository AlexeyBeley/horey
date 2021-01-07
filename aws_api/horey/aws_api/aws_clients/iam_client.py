"""
AWS iam client to handle iam service API requests.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aws_services_entities"))
from iam_user import IamUser
from iam_access_key import IamAccessKey
from iam_policy import IamPolicy
from boto3_client import Boto3Client
from iam_role import IamRole
from common_utils import CommonUtils
import pdb

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
        final_result = list()

        for response in self.execute(self.client.list_users, "Users"):
            user = IamUser(response)
            final_result.append(user)

        if full_information:
            for update_info in self.execute(self.client.get_account_authorization_details, "UserDetailList"):
                user = CommonUtils.find_objects_by_values(final_result, {"id": update_info["UserId"]}, max_count=1)[0]
                user.update_attributes(update_info)

        return final_result



    def get_all_access_keys(self):
        """
        Get all access keys.
        :return:
        """
        final_result = list()
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
        final_result = list()

        for result in self.execute(self.client.list_roles, "Roles", filters_req={"MaxItems": 1000}):
            role = IamRole(result)
            final_result.append(role)
            if full_information:
                self.update_iam_role_full_information(role, policies)

        return final_result

    def update_iam_role_full_information(self, iam_role, policies):
        """
        list_role_policies:
        ('RoleName', '')
        ('PolicyName', '')
        ('PolicyDocument', {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Action': 'ec2:Describe*', 'Resource': '*'}, {'Effect': 'Allow', 'Action': 'elasticloadbalancing:Describe*', 'Resource': '*'},
        {'Effect': 'Allow', 'Action': ['cloudwatch:ListMetrics', 'cloudwatch:GetMetricStatistics', 'cloudwatch:Describe*'], 'Resource': '*'}, {'Effect': 'Allow', 'Action': 'autoscaling:Describe*', 'Resource': '*'}]})
        ('ResponseMetadata', {'RequestId': 'dcc6b611-786c-4ef7-a7d3-a7c391755326', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'dcc6b611-786c-4ef7-a7d3-a7c391755326', 'content-type': 'text/xml',
        'content-length': '1963', 'date': 'Thu, 17 Sep 2020 07:49:30 GMT'}, 'RetryAttempts': 0})

        :param iam_role:
        :param policies:
        :return:
        """

        self.update_iam_role_last_used(iam_role)
        self.update_iam_role_managed_policies(iam_role, policies)
        self.update_iam_role_inline_policies(iam_role)

    def update_iam_role_last_used(self, iam_role):
        """
        Full information part update.
        :param iam_role:
        :return:
        """
        ret = self.execute(self.client.get_role, "Role", filters_req={"RoleName": iam_role.name})
        update_info = next(ret)
        iam_role.update_extended(update_info)

    def update_iam_role_managed_policies(self, iam_role, policies):
        """
        Full information part update.
        :param iam_role:
        :return:
        """
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
                iam_role.add_policy(policy)

                policy_dict = {"Document": document_dict}
                policy.update_statements(policy_dict)

    def get_all_policies(self, full_information=True):
        """
        Get all iam policies.
        :param full_information:
        :return:
        """
        final_result = list()

        for result in self.execute(self.client.list_policies, "Policies"):
            pol = IamPolicy(result)
            if full_information:
                self.update_policy_statements(pol)
            final_result.append(pol)
        return final_result

    def update_policy_statements(self, policy):
        """
        Fetches and pdates the policy statements
        :param policy: The IamPolicy obj
        :return: None, raise if fails
        """
        for response in self.execute(self.client.get_policy_version, "PolicyVersion", filters_req={"PolicyArn": policy.arn, "VersionId": policy.default_version_id}):
            policy.update_statements(response)

    def create_role(self, request_dict):
        for response in self.execute(self.client.create_role, "Role", filters_req=request_dict):
            return response

    def attach_role_policy(self, request_dict):
        for response in self.execute(self.client.attach_role_policy, "Role", filters_req=request_dict, raw_data=True):
            return response
