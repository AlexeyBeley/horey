import os
import sys
import pdb
import pytest

from horey.aws_api.aws_api import AWSAPI

from horey.h_logger import get_logger
logger = get_logger()

from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = "/Users/alexeybe/Desktop/tmp/configuration_values.py"
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)


# region done
@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_lambdas():
    aws_api.init_security_groups(from_cache=True, cache_file=configuration.aws_api_ec2_security_groups_cache_file)
    aws_api.init_lambdas(from_cache=True, cache_file=configuration.aws_api_lambdas_cache_file)
    tb_ret = aws_api.cleanup_report_lambdas(configuration.aws_api_cleanups_lambda_file)
    assert tb_ret is not None
# endregion

@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_cloud_watch_logs():
    aws_api.cleanup_report_cloud_watch_log_groups(configuration.aws_api_cloudwatch_cache_dir)



@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_s3_buckets():
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)

        aws_api.init_s3_buckets(from_cache=True, cache_file=buckets_cache_json_file)

        aws_api.generate_summarised_s3_cleanup_data(S3_PER_BUCKET_OBJECTS_DIR, summarised_data_file)
        aws_api.cleanup_report_s3_buckets_objects(summarised_data_file)


@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_iam_roles():
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)

        aws_api.init_iam_roles(from_cache=True,
                            cache_file="/Users/alexeybe/private/aws_api/ignore/cache_objects/iam_roles.json")

        aws_api.cleanup_report_iam_roles()


@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_iam_policies():
    aws_api.init_iam_policies(from_cache=True, cache_file=IAM_POLICIES_CACHE_FILE)
    aws_api.cleanup_report_iam_policies()


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
