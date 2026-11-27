from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region


def main():
    ret_accounts = {}

    acc_default = AWSAccount()
    acc_default.name = "horey_account"  # Human readable name
    acc_default.id = "12345678910"  # Unique ID. Used to name a directory storing the cache data. I use the AWS Account ID.

    cs1 = AWSAccount.ConnectionStep(
        {"profile": "default", "region_mark": "us-east-1"}
    )  # profile name in ~/.aws/credentials
    acc_default.connection_steps.append(cs1)

    reg = Region()
    reg.region_mark = "us-east-1"
    acc_default.regions[reg.region_mark] = reg

    ret_accounts[acc_default.id] = acc_default

    return ret_accounts
