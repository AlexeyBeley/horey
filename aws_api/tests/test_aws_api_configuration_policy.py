import os
import sys
import pdb
import pytest


from horey.h_logger import get_logger
logger = get_logger()
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy

#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_aws_api_configuration_policy():
    configuration = AWSAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_values.py")
    configuration.init_from_file()

@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_iam_roles():
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)

        aws_api.init_iam_roles(from_cache=True,
                            cache_file="/Users/alexeybe/private/aws_api/ignore/cache_objects/iam_roles.json")

        aws_api.cleanup_report_iam_roles()


#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_lambdas():
    aws_api.init_security_groups(from_cache=True, cache_file=SECURITY_GROUPS_CACHE_FILE)
    aws_api.init_lambdas(from_cache=True, cache_file=LAMBDAS_CACHE_FILE)
    tb_ret = aws_api.cleanup_report_lambdas(CLEANUP_LAMBDAS_REPORT)
    assert tb_ret is not None


@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_iam_policies():
    aws_api.init_iam_policies(from_cache=True, cache_file=IAM_POLICIES_CACHE_FILE)
    aws_api.cleanup_report_iam_policies()


cloud_watch_cache = "cloud_watch_log_groups.json"
cloud_watch_streams = "cloudwatch_log_groups_rnd"

@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_cloud_watch_logs():
    aws_api.cleanup_report_cloud_watch_log_groups(cloudwatch_log_groups_dir)



@pytest.mark.skip(reason="No way of currently testing this")
def test_prepare_hosted_zones_mapping():
    aws_api.init_hosted_zones(from_cache=True,
                              cache_file=HOSTED_ZONES_CACHE_FILE)

    aws_api.prepare_hosted_zones_mapping()
    pdb.set_trace()

if __name__ == "__main__":
    pass
    #test_init_from_cache_and_cleanup_s3_buckets()
    #test_init_from_cache_and_cleanup_lambdas()
    #test_cleanup_report_iam_roles()
    #test_prepare_hosted_zones_mapping()
    #test_cleanup_report_cloud_watch_logs()
