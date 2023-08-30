"""
AWS Cleaner. Money, money, money...

"""

# pylint: disable=no-name-in-module
from collections import defaultdict
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.common_utils.text_block import TextBlock

logger = get_logger()


class AWSCleaner:
    """
    Alert system management class.

    """

    def __init__(self, configuration):
        self.configuration = configuration

        aws_api_configuration = AWSAPIConfigurationPolicy()
        aws_api_configuration.accounts_file = self.configuration.managed_accounts_file_path
        aws_api_configuration.aws_api_account= self.configuration.aws_api_account_name
        self.aws_api = AWSAPI(aws_api_configuration)

    def init_ec2_volumes(self):
        """
        Init EC2 EBS volumes.

        :return:
        """

        if not self.aws_api.ec2_volumes:
            self.aws_api.init_ec2_volumes()

    def cleanup_report_ebs_volumes(self):
        """
        Generate cleanup report for Volumes

        :return:
        """

        tb_ret = TextBlock("EBS Volumes not in use")
        tb_ret_tmp = self.cleanup_report_ebs_volumes_in_use()
        if tb_ret_tmp.blocks or tb_ret_tmp.lines:
            tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.cleanup_report_ebs_volumes_types()
        tb_ret.blocks.append(tb_ret_tmp)
        tb_ret_tmp = self.cleanup_report_ebs_volumes_sizes()
        tb_ret.blocks.append(tb_ret_tmp)
        with open(self.configuration.ec2_ebs_report_file_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(tb_ret.format_pprint())

        logger.info(f"Output in: {self.configuration.ec2_ebs_report_file_path}")
        return tb_ret

    def cleanup_report_ebs_volumes_in_use(self):
        """
        Check volumes not in use

        :return:
        """

        self.init_ec2_volumes()

        tb_ret = TextBlock("EBS Volumes not in use")
        for volume in self.aws_api.ec2_volumes:
            if volume.state == "in-use":
                continue
            try:
                name = volume.get_tagname()
            except RuntimeError as exception_instance:
                if "No tag" not in repr(exception_instance):
                    raise
                name = volume.id
            tb_ret.lines.append(f"{name}: {volume}")
        return tb_ret

    def cleanup_report_ebs_volumes_sizes(self):
        """
        Generate EBS Volume sizes

        :return:
        """

        self.init_ec2_volumes()

        tb_ret = TextBlock("EBS Volumes' sizes")
        for volume in sorted(self.aws_api.ec2_volumes, key=lambda vol: vol.size, reverse=True):
            try:
                name = volume.get_tagname()
            except RuntimeError as exception_instance:
                if "No tag" not in repr(exception_instance):
                    raise
                name = volume.id

            try:
                attachment_string = volume.attachments[0]['InstanceId']
            except IndexError:
                attachment_string = "Not-attached"

            tb_ret.lines.append(
                f"{volume.availability_zone}, {name}, {volume.volume_type}, {volume.size}GB, {volume.iops}IOPS, Attached:{attachment_string}")
        return tb_ret

    def cleanup_report_ebs_volumes_types(self):
        """
        Generate EBS Volume sizes by type.

        :return:
        """

        self.init_ec2_volumes()

        tb_ret = TextBlock("Storage used by type")
        dict_ret = defaultdict(int)
        for volume in self.aws_api.ec2_volumes:
            dict_ret[volume.volume_type] += volume.size
        for volume_type, size in sorted(dict_ret.items(), key=lambda x: x[1]):
            tb_ret.lines.append(
                f"{volume_type}, {size} GB")

        return tb_ret
