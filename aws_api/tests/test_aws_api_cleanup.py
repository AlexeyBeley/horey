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
#configuration.configuration_file_full_path = "/home/ubuntu/configuration_values.py"
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)


# region done
@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_lambdas():
    aws_api.init_security_groups(from_cache=True, cache_file=configuration.aws_api_ec2_security_groups_cache_file)
    aws_api.init_lambdas(from_cache=True, cache_file=configuration.aws_api_lambdas_cache_file)
    aws_api.init_cloud_watch_log_groups(from_cache=True, cache_file=configuration.aws_api_cloudwatch_log_groups_cache_file)
    tb_ret = aws_api.cleanup_report_lambdas(configuration.aws_api_cleanups_lambda_file, configuration.aws_api_cloudwatch_log_groups_streams_cache_dir)
    assert tb_ret is not None


@pytest.mark.skip(reason="No way of currently testing this")
def test_cleanup_report_cloud_watch_logs():
    aws_api.init_cloud_watch_log_groups(from_cache=True, cache_file=configuration.aws_api_cloudwatch_log_groups_cache_file)
    ret = aws_api.cleanup_report_cloud_watch_log_groups(configuration.aws_api_cloudwatch_log_groups_streams_cache_dir, configuration.aws_api_cleanup_cloudwatch_report_file)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_s3_buckets():
    aws_api.init_s3_buckets(from_cache=True, cache_file=configuration.aws_api_s3_buckets_cache_file)
    aws_api.generate_summarised_s3_cleanup_data(configuration.aws_api_s3_bucket_objects_cache_dir, configuration.aws_api_cleanups_s3_summarized_data_file)
    aws_api.cleanup_report_s3_buckets_objects(configuration.aws_api_cleanups_s3_summarized_data_file, configuration.aws_api_cleanups_s3_report_file)

@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_load_balancers():
    aws_api.init_classic_load_balancers(from_cache=True, cache_file=configuration.aws_api_classic_loadbalancers_cache_file)
    aws_api.init_load_balancers(from_cache=True, cache_file=configuration.aws_api_loadbalancers_cache_file)
    aws_api.init_target_groups(from_cache=True, cache_file=configuration.aws_api_loadbalancer_target_groups_cache_file)
    aws_api.cleanup_load_balancers(configuration.aws_api_cleanups_loadbalancers_report_file)


#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_report_iam_policies():
    aws_api.init_iam_policies(from_cache=True, cache_file=configuration.aws_api_iam_policies_cache_file)
    aws_api.init_iam_roles(from_cache=True, cache_file=configuration.aws_api_iam_roles_cache_file)
    aws_api.cleanup_report_iam_policies(configuration.aws_api_cleanups_iam_policies_report_file)

@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_report_iam_roles():
    aws_api.init_iam_roles(from_cache=True, cache_file=configuration.aws_api_iam_roles_cache_file)
    aws_api.cleanup_report_iam_roles(configuration.aws_api_cleanups_iam_roles_report_file)
# endregion

@pytest.mark.skip(reason="No way of currently testing this")
def test_init_from_cache_and_cleanup_report_dns_records():
    aws_api.init_ec2_instances(from_cache=True, cache_file=configuration.aws_api_ec2_instances_cache_file)
    aws_api.init_classic_load_balancers(from_cache=True, cache_file=configuration.aws_api_classic_loadbalancers_cache_file)
    aws_api.init_load_balancers(from_cache=True, cache_file=configuration.aws_api_loadbalancers_cache_file)
    aws_api.init_databases(from_cache=True, cache_file=configuration.aws_api_databases_cache_file)
    aws_api.init_hosted_zones(from_cache=True, cache_file=configuration.aws_api_hosted_zones_cache_file)
    aws_api.init_cloudfront_distributions(from_cache=True, cache_file=configuration.aws_api_cloudfront_distributions_cache_file)
    aws_api.init_s3_buckets(from_cache=True, cache_file=configuration.aws_api_s3_buckets_cache_file)

    aws_api.cleanup_report_dns_records(configuration.aws_api_cleanups_dns_report_file)


@pytest.mark.skip(reason="No way of currently testing this")
def test_prepare_hosted_zones_mapping():
    aws_api.init_hosted_zones(from_cache=True,
                              cache_file=HOSTED_ZONES_CACHE_FILE)

    aws_api.prepare_hosted_zones_mapping()
    pdb.set_trace()

if __name__ == "__main__":
    pass
    test_init_from_cache_and_cleanup_s3_buckets()
    #test_init_from_cache_and_cleanup_s3_buckets()
    #test_init_from_cache_and_cleanup_lambdas()
    #test_cleanup_report_iam_roles()
    #test_prepare_hosted_zones_mapping()
    #test_cleanup_report_cloud_watch_logs()
