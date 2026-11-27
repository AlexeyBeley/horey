from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region


def main():
    ret_accounts = {}
    default_profile_account = AWSAccount()
    default_profile_account.name = "default"
    default_profile_account.id = "default"
    region_marks = ["us-west-2"]
    cs1 = AWSAccount.ConnectionStep({"profile": "default", "region_mark": region_marks[0]})
    default_profile_account.connection_steps.append(cs1)

    for reg_mark in region_marks:
        reg = Region()
        reg.region_mark = reg_mark
        default_profile_account.regions[reg.region_mark] = reg

    ret_accounts[default_profile_account.id] = default_profile_account
    return ret_accounts
