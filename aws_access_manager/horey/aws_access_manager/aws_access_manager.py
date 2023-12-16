"""
AWS Access manager.

"""
import re

from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_access_manager.aws_access_manager_configuration_policy import AWSAccessManagerConfigurationPolicy

logger = get_logger()


class AWSAccessManager:
    """
    Main logic class

    """

    def __init__(self, configuration: AWSAccessManagerConfigurationPolicy):
        self.configuration = configuration

        aws_api_configuration = AWSAPIConfigurationPolicy()
        aws_api_configuration.accounts_file = self.configuration.managed_accounts_file_path
        aws_api_configuration.aws_api_account = self.configuration.aws_api_account_name
        aws_api_configuration.aws_api_cache_dir = configuration.cache_dir
        self.aws_api = AWSAPI(aws_api_configuration)


    def generate_user_aws_api_accounts(self, user_name):
        """
        1. New create_access_key -> credentials
        2. Use credentials to connect AWS.
        3. Find all roles the user can assume. (Find recursive assumption if possible. i.e. You can assume role after assuming role.)
        4. Run all the restricted commands and validate they fail.
        5. Credentials -> delete_access_key

        :param user_name:
        :return:
        """
        lst_ret = []

        user = self.aws_api.find_user_by_name(user_name)
        dict_access_key = self.aws_api.iam_client.create_access_key(user)
        account = AWSAccount()
        step_user = AWSAccount.ConnectionStep({
                        "aws_access_key_id": dict_access_key["AccessKeyId"],
                        "aws_secret_access_key": dict_access_key["SecretAccessKey"]
                        })
        account.connection_steps.append(step_user)
        lst_ret.append(account)

    def get_user_assume_roles(self, user_name):
        """
        Find all the roles a user can assume.

        :param user_name:
        :return:
        """

        user = self.aws_api.find_user_by_name(user_name)
        lst_ret = []
        for role in self.aws_api.iam_client.yield_roles(update_info=False, full_information=False):
            assume_arn_masks = role.get_assume_arn_masks()
            for arn_mask in assume_arn_masks:
                if self.check_arn_mask_match(user.arn, arn_mask):
                    logger.info(f"Role {role.arn} matches assume role mask: {arn_mask}")
                    lst_ret.append(role)
                    break

        return lst_ret

    # pylint: disable= too-many-branches
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

        if "?" in arn:
            raise NotImplementedError(arn)

        if "?" in mask:
            raise NotImplementedError(mask)

        lst_arn = arn.split(":", 5)
        lst_mask = mask.split(":", 5)

        for i, mask_segment in enumerate(lst_mask[:5]):
            if "*" not in mask_segment and "?" not in mask_segment:
                if mask_segment != lst_arn[i]:
                    return False
            else:
                print(i)
                raise NotImplementedError("""
                mask_segment = mask_segment.replace("*", ".*")
                lst_mask[i] = re.compile(mask_segment)""")

        if lst_arn[2] == "iam":
            resource_type, resource_id = AWSAccessManager.extract_resource_type_and_id_from_arn(lst_arn)
            mask_resource_regex, mask_resource_id = AWSAccessManager.extract_resource_type_and_id_regex_from_arn_mask(lst_mask)
        else:
            raise NotImplementedError(f"Did not yet test with these services: {arn=}, {mask=}")

        if mask_resource_regex is not None and not isinstance(mask_resource_regex, str):
            raise NotImplementedError(f"Resource type: {mask=}, {resource_type=}")

        if mask_resource_regex != resource_type:
            return False

        if not isinstance(mask_resource_id, str) or resource_id is None:
            raise NotImplementedError(f"Resource id: {mask=}, {resource_id=}")

        if mask_resource_id != resource_id:
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
        delimiter = None
        resource_type = None
        resource_id = None
        if "/" in resource_type_and_id:
            resource_type, resource_id = resource_type_and_id.split("/")
            delimiter = "/"

        if ":" in resource_type_and_id:
            resource_type, resource_id = resource_type_and_id.split(":")
            delimiter = ":"
        if delimiter is None:
            raise NotImplementedError(f"Delimiter None not implemented: {lst_arn=}")

        if delimiter not in lst_arn[5]:
            raise NotImplementedError(f"No delimiter not implemented: {lst_arn=}")

        return resource_type, resource_id

    @staticmethod
    def extract_resource_type_and_id_regex_from_arn_mask(lst_mask):
        """
        Extract resource type and id regex.

        :param lst_mask:
        :return:
        """
        if lst_mask[2] == "iam":
            delimiter = "/"

            mask_resource_type_and_id = lst_mask[5]
            if delimiter not in mask_resource_type_and_id:
                if mask_resource_type_and_id == "root":
                    mask_resource_type = None
                    mask_resource_id = "root"
                else:
                    raise NotImplementedError(f"Resource type/id is not implemented: {mask_resource_type_and_id}")
            else:
                mask_resource_type, mask_resource_id = mask_resource_type_and_id.split(delimiter)
        else:
            raise ValueError(f"Can not decide what delimiter is: {lst_mask=}")

        if isinstance(mask_resource_type, str) and ("*" in mask_resource_type or "?" in mask_resource_type):
            if mask_resource_type == "*":
                mask_resource_regex = re.compile(".*")
            else:
                raise NotImplementedError(f"Resource type: {lst_mask=}")
        else:
            mask_resource_regex = mask_resource_type

        if "*" in mask_resource_id or "?" in mask_resource_id:
            raise NotImplementedError(f"Resource id: {lst_mask=}")
        return mask_resource_regex, mask_resource_id

    def generate_user_access_report(self):
        """
        Generate users access report.

        :return:
        """
