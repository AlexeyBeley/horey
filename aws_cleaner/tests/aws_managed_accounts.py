"""
This is a sample configuration to restrict AWS access.
I created a [cleaner] profile in ~/.aws/credentials.

"""

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region


def main():
    """
    If you have multiple accounts and need AWS API to switch between them - add by name.
    :return:
    """

    ret_accounts = {}
    # DEV
    development_environment = AWSAccount()
    development_environment.name = "cleaner"
    development_environment.id = "cleaner"

    cs1 = AWSAccount.ConnectionStep({"profile": "cleaner", "region_mark": "us-west-2"})
    development_environment.connection_steps.append(cs1)
    development_environment.regions["us-west-2"] = Region.get_region("us-west-2")

    #cs1 = AWSAccount.ConnectionStep({"profile": "default", "region_mark": "us-east-1"})
    #cs1 = AWSAccount.ConnectionStep({"profile": "cleaner", "region_mark": "us-east-1"})
    #development_environment.connection_steps.append(cs1)
    #development_environment.regions["us-east-1"] = Region.get_region("us-east-1")

    #cs1 = AWSAccount.ConnectionStep({"profile": "default", "region_mark": "us-west-2"})
    #development_environment.connection_steps.append(cs1)
    #development_environment.regions["us-west-2"] = Region.get_region("us-west-2")

    ret_accounts[development_environment.id] = development_environment

    return ret_accounts
