"""
AWS Access manager.

"""
import copy
# pylint: disable= too-many-lines

import json
import os
import re

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_access_manager.aws_access_manager_configuration_policy import AWSAccessManagerConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils
from horey.aws_access_manager.security_domain_tree import SecurityDomainTree
from horey.replacement_engine.replacement_engine import ReplacementEngine

logger = get_logger()


class AWSAccessManager:
    """
    Main logic class

    """

    def __init__(self, configuration: AWSAccessManagerConfigurationPolicy, aws_api):
        self.configuration = configuration

        self.aws_api = aws_api
        self.replacement_engine = ReplacementEngine()

    def get_user_assume_roles(self, user_name):
        """
        Find all the roles a user can assume.

        :param user_name:
        :return:
        """
        if not self.aws_api.iam_roles:
            self.aws_api.init_iam_roles()
        user = self.aws_api.find_user_by_name(user_name)
        return self.get_arn_assume_roles(user.arn)

    def get_arn_assume_roles(self, arn):
        """
        Find all the roles an ARN can assume.

        :param arn:
        :return:
        """

        if not self.aws_api.iam_roles:
            self.aws_api.init_iam_roles()

        lst_ret = []
        for role in self.aws_api.iam_roles:
            assume_arn_masks = role.get_assume_arn_masks()
            for arn_mask in assume_arn_masks:
                if self.check_arn_mask_match(arn, arn_mask):
                    logger.info(f"Role {role.arn} matches assume role mask: {arn_mask}")
                    lst_ret.append(role)
                    break

        return lst_ret

    def get_role_assume_roles(self, src_role):
        """
        Find all the roles a role can assume.

        :param src_role:
        :return:
        """
        if not self.aws_api.iam_roles:
            self.aws_api.init_iam_roles()

        lst_ret = []
        for role in self.aws_api.iam_roles:
            assume_arn_masks = role.get_assume_arn_masks()
            for arn_mask in assume_arn_masks:
                if self.check_arn_mask_match(src_role.arn, arn_mask):
                    logger.info(f"Role {role.arn} matches assume role mask: {arn_mask}")
                    lst_ret.append(role)
                    break

        return lst_ret

    # pylint: disable= too-many-branches, too-many-return-statements
    @staticmethod
    def check_arn_mask_match(arn, mask):
        """
        Check whether the ARN is permitted by mask.
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html

        arn:partition:service:region:account-id:resource-id
        arn:partition:service:region:account-id:resource-type/resource-id
        arn:partition:service:region:account-id:resource-type:resource-id

        ARN:
        Partition
        Service
        Region
        AccountID
        ResourceType (optional – empty string is missing)
        Resource

        :param arn:
        :param mask:
        :return:
        """

        if mask == "*":
            return True

        lst_arn = arn.split(":", 5)
        lst_mask = mask.split(":", 5)

        for i, mask_segment in enumerate(lst_mask[:5]):
            if "*" not in mask_segment and "?" not in mask_segment:
                if mask_segment != lst_arn[i]:
                    return False
            else:
                re_mask_segment = AWSAccessManager.make_regex_from_string(mask_segment)
                if re_mask_segment.fullmatch(lst_arn[i].lower()) is None:
                    return False

        mask_resource_regex, mask_resource_id = AWSAccessManager.extract_resource_type_and_id_regex_from_arn_mask(
            lst_mask)
        resource_type, resource_id = AWSAccessManager.extract_resource_type_and_id_from_arn(lst_arn)

        if mask_resource_regex is not None and not isinstance(mask_resource_regex, str):
            if mask_resource_regex.match(resource_type) is None:
                return False
        elif mask_resource_regex != resource_type:
            return False

        if  resource_id is None:
            raise NotImplementedError(f"Resource id: {mask=}, {resource_id=}")

        if isinstance(mask_resource_id, str):
            if mask_resource_id != resource_id:
                return False
        else:
            if not mask_resource_id.match(resource_id):
                return False

        for i, mask_segment in enumerate(lst_mask[:5]):
            if not isinstance(mask_segment, str):
                raise NotImplementedError(mask_segment)
            if mask_segment != lst_arn[i]:
                return False
        return True

    @staticmethod
    def extract_resource_type_and_id_from_arn(lst_arn):
        """
        Extract resource type and id.

        :param lst_arn:
        :return:
        """
        resource_type_and_id = lst_arn[5]

        if lst_arn[2] == "iam":
            delimiter = "/"
            if resource_type_and_id.count(delimiter) in [2, 3]:
                resource_type, resource_id = resource_type_and_id.split(delimiter, 1)
                if resource_type != "role":
                    raise ValueError(f"Role path supported, received: {lst_arn}")
                return resource_type, resource_id

        elif lst_arn[2] == "lambda":
            delimiter = ":"
        elif lst_arn[2] == "ec2":
            delimiter = "/"
        elif lst_arn[2] == "ecs":
            delimiter = "/"
            if resource_type_and_id.count(delimiter) > 1:
                if resource_type_and_id.startswith("service") or resource_type_and_id.startswith("task"):
                    return resource_type_and_id.split(delimiter, 1)
        elif lst_arn[2] == "sns":
            delimiter = ":"
            if resource_type_and_id.count(delimiter) == 0:
                resource_type, resource_id = "topic", resource_type_and_id
                return resource_type, resource_id
            if resource_type_and_id.count(delimiter) == 1:
                raise RuntimeError("""
                resource_type, resource_id = "subscription", resource_type_and_id
                return resource_type, resource_id
                """)
            raise NotImplementedError(f"sns has shitty arn convention, not implemented: {lst_arn}")
        else:
            raise NotImplementedError(f"Did not yet test with these services: {lst_arn=}")

        if delimiter in resource_type_and_id:
            resource_type, resource_id = resource_type_and_id.split(delimiter)
        else:
            raise NotImplementedError(f"No delimiter not implemented: {lst_arn=}")

        return resource_type, resource_id

    # pylint: disable= too-many-statements
    @staticmethod
    def extract_resource_type_and_id_regex_from_arn_mask(lst_mask):
        """
        Extract resource type and id regex.

        :param lst_mask:
        :return:
        """

        mask_resource_type, mask_resource_id = None, None
        mask_resource_type_and_id = lst_mask[5]

        if lst_mask[2] == "iam":
            delimiter = "/"

            if delimiter not in mask_resource_type_and_id:
                if mask_resource_type_and_id == "root":
                    mask_resource_type = None
                    mask_resource_id = "root"
                elif mask_resource_type_and_id == "*":
                    mask_resource_type = "*"
                    mask_resource_id = "*"
                else:
                    raise NotImplementedError(f"Resource type/id is not implemented: {mask_resource_type_and_id}")

            elif mask_resource_type_and_id.count(delimiter) in [2, 3]:
                mask_resource_type, mask_resource_id = mask_resource_type_and_id.split(delimiter, 1)
                if mask_resource_type != "role":
                    raise ValueError(f"Role path supported, received: {lst_mask}")
        elif lst_mask[2] == "lambda":
            delimiter = ":"
            if mask_resource_type_and_id.count(delimiter) == 2:
                mask_resource_type, mask_resource_id = mask_resource_type_and_id.split(delimiter, 1)
        elif lst_mask[2] == "ec2":
            delimiter = "/"
        elif lst_mask[2] == "ecs":
            delimiter = "/"
            if mask_resource_type_and_id.count(delimiter) > 1:
                mask_resource_type, mask_resource_id = mask_resource_type_and_id.split(delimiter, 1)
                if mask_resource_type not in ["task", "task-set", "service"]:
                    raise NotImplementedError(f"Wasn't checked for {mask_resource_type}")
        elif lst_mask[2] == "sns":
            delimiter = ":"
            if mask_resource_type_and_id.count(delimiter) == 0:
                if mask_resource_type_and_id != "*":
                    # Problem sns_topic_name* is not on;y topic but all its subscriptions....
                    mask_resource_type, mask_resource_id = "topic", mask_resource_type_and_id
                else:
                    mask_resource_type, mask_resource_id = "*", "*"
            elif mask_resource_type_and_id.count(delimiter) == 1:
                raise NotImplementedError("""
                resource_type, resource_id = "subscription", mask_resource_type_and_id
                return resource_type, resource_id
                """)
            else:
                raise NotImplementedError(f"sns has shitty arn convention, not implemented: {lst_mask}")
        else:
            raise ValueError(f"Can not decide what delimiter is: {lst_mask=}")

        if mask_resource_type is None and mask_resource_id is None:
            if delimiter not in mask_resource_type_and_id:
                if mask_resource_type_and_id == "*":
                    mask_resource_type, mask_resource_id = "*", "*"
                else:
                    raise NotImplementedError(f"No delimiter in {mask_resource_type_and_id}")
            else:
                mask_resource_type, mask_resource_id = mask_resource_type_and_id.split(delimiter)

        if isinstance(mask_resource_type, str) and ("*" in mask_resource_type or "?" in mask_resource_type):
            mask_resource_regex = AWSAccessManager.make_regex_from_string(mask_resource_type)
        else:
            mask_resource_regex = mask_resource_type

        if "*" in mask_resource_id:
            mask_resource_id = AWSAccessManager.make_regex_from_string(mask_resource_id)

        return mask_resource_regex, mask_resource_id

    @staticmethod
    def make_regex_from_string(str_src):
        """
        Make regex from string.

        :param str_src:
        :return:
        """

        if "?" in str_src:
            raise NotImplementedError(f"String contains '?': {str_src=}")

        str_regex = "^" + str_src.lower().replace("*", ".*") + "$"

        return re.compile(str_regex)

    def generate_users_access_report(self):
        """
        Generate users access report.

        :return:
        """

    def generate_user_aws_api_accounts(self, aws_access_key_id, aws_secret_access_key, roles):
        """
        Generate all user accounts.

        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param roles:
        :return:
        """

        ret = [AWSAccessManager.generate_user_credentials_account(aws_access_key_id, aws_secret_access_key)] +\
        AWSAccessManager.generate_user_assume_roles_accounts(aws_access_key_id, aws_secret_access_key, roles)
        for role in roles:
            role_assumable_roles = self.get_role_assume_roles(role)
            for role_assumable_role in role_assumable_roles:
                new_accounts = AWSAccessManager.generate_user_assume_roles_accounts(aws_access_key_id, aws_secret_access_key, [role])
                step_assume_role = AWSAccount.ConnectionStep({"assume_role": role_assumable_role.arn})
                new_accounts[0].connection_steps.append(step_assume_role)
                ret += new_accounts

        return ret

    @staticmethod
    def generate_user_credentials_account(aws_access_key_id, aws_secret_access_key):
        """
        Vanila credentials.

        :param aws_access_key_id:
        :param aws_secret_access_key:
        :return:
        """

        aws_api_account = AWSAccount()
        aws_api_account.id = f"User-{aws_access_key_id}"
        aws_api_account.name = aws_api_account.id
        step_user_credentials = AWSAccount.ConnectionStep({
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key
        })
        aws_api_account.connection_steps.append(step_user_credentials)
        return aws_api_account

    @staticmethod
    def generate_user_assume_roles_accounts(aws_access_key_id, aws_secret_access_key, roles):
        """
        Generate aws api accounts.

        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param roles:
        :return:
        """

        step_user_credentials = AWSAccount.ConnectionStep({
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key
        })

        lst_ret = []
        for role in roles:
            aws_api_account = AWSAccount()
            aws_api_account.id = role.name
            aws_api_account.name = role.name
            aws_api_account.connection_steps.append(step_user_credentials)
            step_assume_role = AWSAccount.ConnectionStep({"assume_role": role.arn})
            aws_api_account.connection_steps.append(step_assume_role)
            lst_ret.append(aws_api_account)

        return lst_ret

    def provision_iam_role_lambdas_assumable_roles(self, region, role):
        """
        Prepare a copy of role used by Lambdas accessible with this role.

        :param region:
        :param role:
        :return:
        """
        if not self.aws_api.iam_roles:
            self.aws_api.init_iam_roles()

        aws_lambdas = self.get_iam_role_lambdas(region, role)
        lst_ret = []
        for aws_lambda in aws_lambdas:
            lambda_role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles, {"arn": aws_lambda.role},
                                                             max_count=1)
            if not lambda_role:
                raise NotImplementedError(aws_lambda.role)
            lambda_role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles, {"arn": aws_lambda.role}, max_count=1)[0]
            lambda_role.assume_role_policy_document = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": role.arn}, "Action": "sts:AssumeRole"}]}
            lambda_role.description = "Horey test credentials copy role"
            lambda_role.name += "-hrycrdtst"
            lambda_role.arn = None
            if lambda_role.inline_policies:
                raise NotImplementedError(aws_lambda.role)
                #lambda_role.inline_policies = [IamPolicy(dict_src, from_cache=True) for dict_src in lambda_role.inline_policies]
            self.aws_api.provision_iam_role(lambda_role)
            lst_ret.append(lambda_role)
        return lst_ret

    def get_iam_role_lambdas(self, region, role):
        """
        Get all AWS lambdas the role allowed to run.

        :param region:
        :param role:
        :return:
        """

        policies = self.aws_api.iam_client.get_all_policies(full_information=True)
        lambdas = self.aws_api.lambda_client.get_region_lambdas(region, full_information=True)
        lambdas = [aws_lambda for aws_lambda in lambdas if self.check_role_can_run_lambda(role, aws_lambda, policies)]
        logger.info(f"Role can run {len(lambdas)} lambdas in region: {region.region_mark}")
        return lambdas

    def check_role_can_run_lambda(self, role, aws_lambda, policies):
        """
        # todo: Active check whether can run

        request = {"FunctionName": aws_lambda.name,
                   "InvocationType": "DryRun"
                   }
        AWSAccount.set_aws_region(aws_lambda.region)
        self.aws_api.lambda_client.invoke_raw(request)

        Checks if the iam role can run this AWS Lambda.

        UpdateFunctionConfiguration? grant.

        :param role:
        :param aws_lambda:
        :param policies:
        :return:
        """

        role_policies = [IamPolicy(dict_src, from_cache=True) for dict_src in role.inline_policies]

        for arn in role.managed_policies_arns:
            policy = CommonUtils.find_objects_by_values(policies, {"arn": arn}, max_count=1)[0]
            role_policies.append(policy)

        for role_policy in role_policies:
            if self.check_policy_can_run_lambda(role_policy, aws_lambda):
                return True

        return False

    def check_policy_can_run_lambda(self, policy, aws_lambda):
        """
        Analyze policy document whether it can run the AWS Lambda.

        :param policy:
        :param aws_lambda:
        :return:
        """

        actions = ["InvokeFunction", "InvokeAsync", "InvokeFunctionUrl"]
        for statement in policy.document.statements:
            if not self.check_statement_permits_resource(aws_lambda.arn, statement):
                continue

            if not any(self.check_statement_permits_service_action("lambda", action, statement) for action in actions):
                continue

            if statement.effect != statement.Effects.ALLOW:
                raise NotImplementedError(statement.effect)
            return True

        return False

    def check_statement_action_match(self, statement_action, action):
        """
        Check if the action is approved by statement.

        :param statement_action:
        :param action:
        :return:
        """

        if "*" in statement_action:
            regex_statement_action = self.make_regex_from_string(statement_action)
            if regex_statement_action.fullmatch(action.lower()):
                return True
            return False

        return statement_action == action

    def generate_users_security_domain_tree(self):
        """
        Generate all users report.

        :return:
        """

        lst_ret = []
        for user in self.aws_api.users:
            tree = self.generate_user_security_domain_tree(user)
            with open (os.path.join(self.configuration.user_reports_dir_path, user.name.replace(".", "_")), "w", encoding="utf-8") as file_handler:
                json.dump(tree.convert_to_dict(), file_handler)
            lst_ret.append(tree)
        return lst_ret

    def generate_users_security_domain_graphs(self):
        """
        Generate all users report.

        :return:
        """

        lst_ret = []
        aggressive_dir_path = os.path.join(self.configuration.user_reports_dir_path, "aggressive")
        not_aggressive_dir_path = os.path.join(self.configuration.user_reports_dir_path, "not_aggressive")
        os.makedirs(aggressive_dir_path, exist_ok=True)
        os.makedirs(not_aggressive_dir_path, exist_ok=True)

        for user in self.aws_api.users:
            tree = self.generate_user_security_domain_tree(user)
            dict_graph = tree.generate_security_domain_graph()
            file_name = user.name.replace(".", "_") + "_graph.json"
            file_full_path = os.path.join(self.configuration.user_reports_dir_path, aggressive_dir_path if tree.aggressive else not_aggressive_dir_path, file_name)
            with open (file_full_path, "w", encoding="utf-8") as file_handler:
                json.dump(dict_graph, file_handler)
            logger.info(f"UI graph in {file_full_path}")
            lst_ret.append(tree)
        return lst_ret

    def generate_user_security_domain_tree(self, user):
        """

        :param user:
        :return:
        """

        self.aws_api.init_iam_roles()
        self.aws_api.init_iam_policies()
        self.aws_api.init_iam_groups()
        self.aws_api.init_lambdas(full_information=True)

        direct_policies = self.get_user_direct_policies(user)
        root = SecurityDomainTree.Node(user.arn, "User credentials", direct_policies)
        tree = SecurityDomainTree(root, aggressive=False)
        self.aws_api.init_ec2_instances()
        self.aws_api.init_iam_instance_profiles()
        self.aws_api.init_sns_topics()
        self.aws_api.init_sns_subscriptions()
        self.aws_api.init_ecs_clusters()
        self.aws_api.init_ecs_tasks()
        self.aws_api.init_ecs_services()
        self.aws_api.init_ecs_task_definitions()
        self.extend_security_domain_tree(root, tree)

        return tree

    def get_user_direct_policies(self, user):
        """
        Group inline or attached polices.

        :param user:
        :return:
        """
        lst_ret = []
        for dict_group in user.groups:
            group = CommonUtils.find_objects_by_values(self.aws_api.iam_groups, {"name": dict_group["GroupName"]},  max_count=1)[0]
            for dict_attached_policy in group.attached_policies:
                policy = CommonUtils.find_objects_by_values(self.aws_api.iam_policies,
                                                           {"arn": dict_attached_policy["PolicyArn"]},
                                                           max_count=1)[0]
                lst_ret.append(policy)

            if group.policies:
                lst_ret += [IamPolicy(dict_policy) for dict_policy in group.policies]

        return lst_ret

    def get_role_direct_policies(self, role: IamRole):
        """
        Get role attached and inline policies.

        :param role:
        :return:
        """

        lst_ret = []
        for arn in role.managed_policies_arns:
            policy = CommonUtils.find_objects_by_values(self.aws_api.iam_policies,
                                                           {"arn": arn},
                                                           max_count=1)[0]
            lst_ret.append(policy)

        lst_ret += role.inline_policies

        return lst_ret

    def extend_security_domain_tree(self, node, tree):
        """
        Generate a tree with specific user as a root.
        Basic:
        * User Group permissions.
        * Users a user can generate Access key for.
        * Roles the user can assume.
        * Roles the user can pass.
        * Lambdas the user can change.
        * EC2 user data,
        * Update task definition
        * EKS.


        Aggressive:
        EC2 profile. (User can SSH / RDP to an instance)
        2. Lambdas the user can Invoke
        SNS topic user can send.
        SQS user can send.
        RDS with access to AWS lambda
        6. ECS run task, create service, scheduled task.

        :param node:
        :param tree:
        :return:
        """

        candidate_nodes = self.get_node_reachable_assume_role_nodes(node)
        for policy in node.policies:
            candidate_nodes += self.get_policy_reachable_user_nodes(policy)
            candidate_nodes += self.get_policy_reachable_role_nodes(policy)
            candidate_nodes += self.get_policy_reachable_lambda_role_nodes(policy, aggressive=tree.aggressive)
            candidate_nodes += self.get_policy_reachable_ec2_instance_role_nodes(policy, aggressive=tree.aggressive)
            candidate_nodes += self.get_policy_reachable_ecs_role_nodes(policy, aggressive=tree.aggressive)
            if tree.aggressive:
                candidate_nodes += self.get_policy_reachable_sns_topic_lambdas_role_nodes(policy)

        if tree.aggressive:
            candidate_nodes += self.get_all_ec2_instances_reachable_role_nodes()

        for candidate_node in candidate_nodes:
            if candidate_node.id in tree.node_ids:
                continue
            tree.add_child(node, candidate_node)

        for child_node in node.children:
            self.extend_security_domain_tree(child_node, tree)

        return True

    def get_node_reachable_assume_role_nodes(self, node):
        """
        Get all nodes reachable from the source node by "assume role" mechanism.
        # to do: check if node can UpdateAssumeRolePolicy on roles.

        :param node:
        :return:
        """

        assumable_roles = self.get_arn_assume_roles(node.id)
        lst_ret = []
        for role in assumable_roles:
            node = SecurityDomainTree.Node(role.arn, "AssumeRole",
                                               self.get_role_direct_policies(role))
            lst_ret.append(node)

        return lst_ret

    def get_policy_reachable_role_nodes(self, policy):
        """
        Get IAM-Role-Nodes reachable threw source-policy PassRole permissions

        :param policy: 
        :return:
        """

        lst_ret = []
        for role in self.aws_api.iam_roles:
            statement= self.check_policy_permits_resource_action(policy, role.arn, "PassRole")
            if statement is not None:
                if hasattr(statement, "sid"):
                    sid = f":{statement.sid}"
                else:
                    sid = ""
                node = SecurityDomainTree.Node(role.arn, f"Policy: {policy.name}-> {sid}-> PassRole",
                                               self.get_role_direct_policies(role))
                lst_ret.append(node)

        return lst_ret

    def get_policy_reachable_sns_topic_lambdas_role_nodes(self, policy):
        """
        Get IAM-Role-Nodes reachable using the source-policy on SNS topic

        :param policy:
        :return:
        """

        lst_ret = []
        permissions = ["Publish"]

        for sns_topic in self.aws_api.sns_topics:
            for permission in permissions:
                if not self.check_policy_permits_resource_action(policy, sns_topic.arn, permission):
                    continue
                for subscription in self.aws_api.sns_subscriptions:
                    if subscription.topic_arn != sns_topic.arn:
                        continue
                    if subscription.protocol != "lambda":
                        continue
                    aws_lambda = CommonUtils.find_objects_by_values(self.aws_api.lambdas, {"arn": subscription.endpoint}, max_count=1)[0]
                    node = self.construct_tree_node_from_aws_lambda(aws_lambda, f"Policy {policy.name} permits {permission} on sns topic {sns_topic.arn} triggering lambda {sns_topic.arn}")

                    lst_ret.append(node)
                break

        return lst_ret

    def get_all_ec2_instances_reachable_role_nodes(self):
        """
        Get all roles attached to all instances.

        :return:
        """
        lst_ret = []

        for ec2_instance in self.aws_api.ec2_instances:
            if ec2_instance.iam_instance_profile is None:
                continue

            instance_profile_arn = ec2_instance.iam_instance_profile["Arn"]
            instance_profile = CommonUtils.find_objects_by_values(self.aws_api.iam_instance_profiles, {"arn": instance_profile_arn}, max_count=1)[0]
            for dict_role in instance_profile.roles:
                role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles,
                                                                        {"arn": dict_role["Arn"]},
                                                                      max_count=1)[0]
                node = SecurityDomainTree.Node(role.arn,
                                                f"SSH-> {ec2_instance.arn}-> {instance_profile_arn}",
                                               self.get_role_direct_policies(role))
                lst_ret.append(node)

        return lst_ret

    def get_policy_reachable_ec2_instance_role_nodes(self, policy, aggressive=True):
        """
        Get IAM-Role-Nodes reachable by a resource using the source-policy on EC2 instances.
        ModifyInstanceAttribute - modify user data

        :param policy:
        :param aggressive:
        :return:
        """

        lst_ret = []
        permissions = ["CreateInstanceConnectEndpoint", "ModifyInstanceAttribute"]

        if aggressive:
            permissions += ["RunInstances", "StartInstances"]

        for ec2_instance in self.aws_api.ec2_instances:
            if ec2_instance.iam_instance_profile is None:
                continue

            for permission in permissions:
                statement = self.check_policy_permits_resource_action(policy, ec2_instance.arn, permission, ignore_condition=False)
                if statement:
                    instance_profile_arn = ec2_instance.iam_instance_profile["Arn"]
                    instance_profile = CommonUtils.find_objects_by_values(self.aws_api.iam_instance_profiles, {"arn": instance_profile_arn}, max_count=1)[0]
                    for dict_role in instance_profile.roles:
                        role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles,
                                                                              {"arn": dict_role["Arn"]},
                                                                              max_count=1)[0]
                        node = SecurityDomainTree.Node(role.arn,
                                                       f"Policy: {policy.name}-> [{permission}-> {ec2_instance.arn}]",
                                                       self.get_role_direct_policies(role))
                        lst_ret.append(node)
                    break

        return lst_ret

    def get_policy_reachable_ecs_role_nodes(self, policy, aggressive=True):
        """
        Get IAM-Role-Nodes reachable by a resource using the source-policy on ECS resources

        :param policy:
        :param aggressive:
        :return:
        """

        lst_ret = self.get_policy_reachable_ecs_service_role_nodes(policy) + \
                self.get_policy_reachable_ecs_task_role_nodes(policy)

        if aggressive:
            lst_ret += self.get_policy_reachable_ecs_td_role_nodes(policy)

        return lst_ret

    def get_policy_reachable_ecs_service_role_nodes(self, policy):
        """
        Get IAM-Role-Nodes reachable by a resource using the source-policy on ECS service


        :param policy:
        :return:
        """
        lst_ret = []
        permissions = ["UpdateService"]
        for ecs_service in self.aws_api.ecs_services:
            if ecs_service.role_arn is None:
                continue

            for permission in permissions:
                statement = self.check_policy_permits_resource_action(policy, ecs_service.arn, permission, ignore_condition=False)
                if statement:
                    role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles,
                                                              {"arn": ecs_service.role_arn},
                                                              max_count=1)[0]
                    node = SecurityDomainTree.Node(role.arn,
                                                   f"Policy {policy.name}-> {permission}-> {ecs_service.arn}",
                                                   self.get_role_direct_policies(role))
                    lst_ret.append(node)
                    break
        return lst_ret

    def get_policy_reachable_ecs_td_role_nodes(self, policy):
        """
        Get IAM-Role-Nodes reachable by a resource using the source-policy on ECS task definitions


        :param policy:
        :return:
        """

        lst_ret = []
        permissions = ["RunTask", "StartTask"]

        for task_definition in self.aws_api.ecs_task_definitions:
            if task_definition.task_role_arn is None:
                continue

            for permission in permissions:
                statement = self.check_policy_permits_resource_action(policy, task_definition.arn, permission, ignore_condition=False)
                if statement:
                    try:
                        role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles,
                                                              {"arn": task_definition.task_role_arn},
                                                              max_count=1)[0]
                    except IndexError:
                        break
                    node = SecurityDomainTree.Node(role.arn,
                                                   f"Policy: {policy.name}-> {permission}-> {task_definition.arn}",
                                                   self.get_role_direct_policies(role))
                    lst_ret.append(node)
                    break

        return lst_ret

    def get_policy_reachable_ecs_task_role_nodes(self, policy):
        """
        Get IAM-Role-Nodes reachable by a resource using the source-policy on ECS tasks


        :param policy:
        :return:
        """

        lst_ret = []
        permissions = ["ExecuteCommand"]

        for task in self.aws_api.ecs_tasks:
            if task.last_status != "RUNNING":
                continue
            task_definition = CommonUtils.find_objects_by_values(self.aws_api.ecs_task_definitions, {"arn": task.task_definition_arn}, max_count=1)[0]
            if task_definition.task_role_arn is None:
                continue

            for permission in permissions:
                statement = self.check_policy_permits_resource_action(policy, task.arn, permission, ignore_condition=False)
                if statement:
                    role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles,
                                                              {"arn": task_definition.task_role_arn},
                                                              max_count=1)[0]
                    node = SecurityDomainTree.Node(role.arn,
                                                   f"Role: {role.name}-> Policy: {policy.name}-> {permission}-> {task.arn}-> {task.task_definition_arn}",
                                                   self.get_role_direct_policies(role))
                    lst_ret.append(node)
                    break

        return lst_ret

    def get_policy_reachable_lambda_role_nodes(self, policy, aggressive=True):
        """
        Get IAM-Role-Nodes reachable by a resource using the source-policy on Lambdas

        :param policy:
        :param aggressive:
        :return:
        """

        lst_ret = []
        permissions = ["UpdateFunctionCode"]
        if aggressive:
            permissions += ["PublishVersion", "PublishLayerVersion", "InvokeFunctionUrl", "InvokeFunction"]

        for aws_lambda in self.aws_api.lambdas:
            for permission in permissions:
                if self.check_policy_permits_resource_action(policy, aws_lambda.arn, permission, ignore_condition=False):
                    node = self.construct_tree_node_from_aws_lambda(aws_lambda, f"Policy: {policy.name}-> {permission}-> {aws_lambda.arn}")
                    lst_ret.append(node)
                    break

        return lst_ret

    def construct_tree_node_from_aws_lambda(self, aws_lambda, access_type_comment):
        """
        Generate node

        :param aws_lambda:
        :param access_type_comment:
        :return:
        """

        role = CommonUtils.find_objects_by_values(self.aws_api.iam_roles, {"arn": aws_lambda.role}, max_count=1)[0]
        node = SecurityDomainTree.Node(aws_lambda.role,
                                   access_type_comment,
                                   self.get_role_direct_policies(role))
        return node

    def get_policy_reachable_user_nodes(self, policy, aggressive=True):
        """
        Get user-nodes the source-policy grants access to manage.
        e.g. CreateAccessKey
        # to do: AttachUserPolicy

        Aggressive:
        UpdateAccessKey. Preliminary information: Identity using this policy has access to these credentials.

        :param policy:
        :param aggressive:
        :return:
        """
        lst_permissions = ["CreateLoginProfile", "CreateAccessKey", "UpdateLoginProfile"]
        lst_users = []

        for user in self.aws_api.users:
            for permission in lst_permissions:
                if self.check_policy_permits_resource_action(policy, user.arn, permission):
                    lst_users.append(user)
                    break

        lst_ret = []
        for user in lst_users:
            node = SecurityDomainTree.Node(user.arn, f"Policy: {policy.name}-> CreateAccessKey-> {user.name}", self.get_user_direct_policies(user))
            lst_ret.append(node)

        if aggressive:
            lst_users = [user for user in self.aws_api.users if
                         self.check_policy_permits_resource_action(policy, user.arn, "UpdateAccessKey")]
            for user in lst_users:
                node = SecurityDomainTree.Node(user.arn, f"Policy: {policy.name}-> UpdateAccessKey-> {user.name}",
                                               self.get_user_direct_policies(user))
                lst_ret.append(node)


        return lst_ret

    def check_policy_permits_resource_action(self, policy, resource_arn, action, ignore_condition=True):
        """
        Checks if there is a statement permits the action.
        Return Statement if any, None else.

        :param policy:
        :param resource_arn:
        :param action:
        :param ignore_condition:
        :return:
        """

        lst_arn = resource_arn.split(":")
        service = lst_arn[2]
        for statement in policy.document.statements:
            if not self.check_statement_permits_resource(resource_arn, statement):
                continue

            if not self.check_statement_permits_service_action(service, action, statement):
                continue

            if not ignore_condition and not self.check_statement_permits_condition(lst_arn, statement):
                continue

            if statement.effect != statement.Effects.ALLOW:
                raise NotImplementedError(statement.effect)
            return statement
        return None

    def check_statement_permits_resource(self, arn, statement):
        """
        Check policy statement matches arn.

        :param arn:
        :param statement:
        :return:
        """

        if statement.resource:
            resources = [statement.resource] if isinstance(statement.resource, str) else statement.resource
            for resource in resources:
                if self.check_arn_mask_match(arn, resource):
                    break
            else:
                return False
        elif statement.not_resource:
            resources = [statement.not_resource] if isinstance(statement.not_resource, str) else statement.not_resource
            for resource in resources:
                if self.check_arn_mask_match(arn, resource):
                    return False
        else:
            raise ValueError(f"Statement has no resource or not_resource: {statement.dict_src}")

        return True

    def check_statement_permits_service_action(self, service_name, action, statement):
        """
        Check statement allows service:action.

        :param service_name:
        :param action:
        :param statement:
        :return:
        """

        for statement_service, statement_action in statement.action.items():
            if statement_action == "*" and statement_service == "*":
                return True
            if "*" in statement_service:
                raise NotImplementedError(statement_service)
            if statement_service != service_name:
                return False

            statement_actions = [statement_action] if isinstance(statement_action, str) else statement_action
            if any(self.check_statement_action_match(statement_action, action) for statement_action in statement_actions):
                return True

        return False

    def check_statement_permits_condition(self, lst_arn, statement):
        """
        Check policy statement matches arn.

        :param lst_arn:
        :param statement:
        :return:
        """

        if not statement.condition:
            return True

        if len(statement.condition) != 1:
            raise NotImplementedError(statement.condition)

        if "StringEquals" in statement.condition or "StringEqualsIfExists" in statement.condition :
            logical_condition = "StringEquals" if "StringEquals" in statement.condition else "StringEqualsIfExists"
            if len(statement.condition[logical_condition]) != 1:
                raise NotImplementedError(statement.condition)
            if "ec2:Region" in statement.condition[logical_condition]:
                if lst_arn[2] != "ec2":
                    return False
                region_mask = statement.condition["StringEquals"]["ec2:Region"]
                if "*" not in region_mask and "?" not in region_mask:
                    return lst_arn[3] == region_mask
            elif "iam:PassedToService" in statement.condition[logical_condition]:
                service_masks = statement.condition[logical_condition]["iam:PassedToService"]
                service_masks = [service_masks] if isinstance(service_masks, str) else service_masks
                for service_mask in service_masks:
                    if "ec2" in service_mask:
                        return True
                    if "autoscaling" in service_mask or "ssm" in service_mask:
                        return False

        if "StringLike" in statement.condition:
            if len(statement.condition["StringLike"]) != 1:
                raise NotImplementedError(statement.condition)
            if "iam:PassedToService" in statement.condition["StringLike"]:
                service_mask = statement.condition["StringLike"]["iam:PassedToService"]
                if "ec2" in service_mask:
                    return True

        raise NotImplementedError(statement.condition)

    def generate_policy_documents_from_string(self, str_src):
        """
        Split state

        :param str_src:
        :return:
        """

        statements = json.loads(str_src)
        base_document = {
            "Version": "2012-10-17",
            "Statement": []
        }

        ret_documents = []
        current_document = copy.deepcopy(base_document)
        while len(statements) > 0:
            statement = statements.pop(0)
            if len(json.dumps(current_document, indent=4)) + len(json.dumps(statement, indent=4)) > 6144:
                ret_documents.append(json.dumps(current_document))
                current_document = copy.deepcopy(base_document)
            current_document["Statement"].append(statement)

        if current_document["Statement"]:
            ret_documents.append(json.dumps(current_document))

        return ret_documents

    def generate_policy_documents_from_template_file(self, template_file_path, dict_replacements):
        """
        Make all replacements and break to chunks.

        :return:
        """

        logger.info(f"Provisioning deployer policies from file {template_file_path}")
        with open(template_file_path, encoding="utf-8") as file_handler:
            str_src = file_handler.read()

        str_src = self.replacement_engine.perform_replacements_raw(str_src, dict_replacements)

        return self.generate_policy_documents_from_string(str_src)

    def provision_policies_from_template_file(self, template_file_path, dict_replacements, template_policy):
        """
        Provision policies from template file
        !!! template_policy has invalid name with format {} set for counter.
        !!! template_policy should not have "name" tag.

        :return:
        """
        logger.info(f"Provisioning deployer policies from file {template_file_path}")
        policy_documents = self.generate_policy_documents_from_template_file(template_file_path, dict_replacements)
        policies = []
        for i, policy_document in enumerate(policy_documents):
            if policy_document is None:
                continue
            cached_policy = template_policy.convert_to_dict()
            cached_policy["document"] = json.loads(policy_document)
            policy_new = IamPolicy(cached_policy, from_cache=True)
            policy_new.name = template_policy.name.format(i)
            policy_new.tags.append({
                "Key": "name",
                "Value": policy_new.name
            })
            self.aws_api.iam_client.provision_policy(policy_new)
            policies.append(policy_new)
        return policies
