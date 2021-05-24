"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""
import json
import sys
sys.path.insert(0, "/Users/alexey.beley/private/horey/aws_api")
import pdb

import pytest
import os
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
#Uncomment next line to save error lines to /tmp/error.log
configuration_values_file_full_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")

logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "aws_api_configuration_values.py"))
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)


# region done
@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_iam_policies():
    aws_api.init_iam_policies()
    aws_api.cache_objects(aws_api.iam_policies, configuration.aws_api_iam_policies_cache_file)
    logger.info(f"len(iam_policies) = {len(aws_api.iam_policies)}")
    assert isinstance(aws_api.iam_policies, list)


@pytest.mark.skip(reason="IAM roles will be inited explicitly")
def test_init_and_cache_iam_roles():
    aws_api.init_iam_policies(from_cache=True, cache_file=configuration.aws_api_iam_policies_cache_file)
    aws_api.init_iam_roles()
    aws_api.cache_objects(aws_api.iam_roles, configuration.aws_api_iam_roles_cache_file)

    print(f"len(iam_roles) = {len(aws_api.iam_roles)}")
    assert isinstance(aws_api.iam_roles, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_network_interfaces():
    aws_api.init_network_interfaces()
    aws_api.cache_objects(aws_api.network_interfaces, configuration.aws_api_ec2_network_interfaces_cache_file)
    logger.info(f"len(network_interfaces) = {len(aws_api.network_interfaces)}")
    assert len(aws_api.network_interfaces) > 0


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_security_groups():
    aws_api.init_security_groups()
    aws_api.cache_objects(aws_api.security_groups, configuration.aws_api_ec2_security_groups_cache_file)
    logger.info(f"len(security_groups) = {len(aws_api.security_groups)}")
    assert len(aws_api.security_groups) > 0


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_lambdas():
    aws_api.init_lambdas()
    aws_api.cache_objects(aws_api.lambdas, configuration.aws_api_lambdas_cache_file)
    logger.info(f"len(lambdas) = {len(aws_api.lambdas)}")
    assert isinstance(aws_api.lambdas, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_raw_large_cloud_watch_log_groups():
    aws_api.init_and_cache_raw_large_cloud_watch_log_groups(configuration.aws_api_cloudwatch_log_groups_streams_cache_dir)
    print(f"len(cloud_watch_log_groups) = {len(aws_api.cloud_watch_log_groups)}")
    assert isinstance(aws_api.cloud_watch_log_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudwatch_logs():
    aws_api.init_cloud_watch_log_groups()
    aws_api.cache_objects(aws_api.cloud_watch_log_groups, configuration.aws_api_cloudwatch_log_groups_cache_file)
    print(f"len(cloud_watch_log_groups) = {len(aws_api.cloud_watch_log_groups)}")
    assert isinstance(aws_api.cloud_watch_log_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudwatch_log_groups_metric_filters():
    aws_api.init_cloud_watch_log_groups_metric_filters()
    aws_api.cache_objects(aws_api.cloud_watch_log_groups_metric_filters, configuration.aws_api_cloudwatch_log_groups_metric_filters_cache_file)
    print(f"len(cloud_watch_log_group_metric_filters) = {len(aws_api.cloud_watch_log_groups_metric_filters)}")
    assert isinstance(aws_api.cloud_watch_log_groups_metric_filters, list)


@pytest.mark.skip(reason="No way of currently testing cloudwatch metrics")
def test_init_and_cache_cloudwatch_metrics():
    aws_api.cache_raw_cloud_watch_metrics(configuration.aws_api_cloudwatch_metrics_cache_dir)


@pytest.mark.skip(reason="No way of currently testing cloudwatch metrics")
def test_init_and_cache_cloudwatch_alarms():
    aws_api.init_cloud_watch_alarms()
    aws_api.cache_objects(aws_api.cloud_watch_alarms, configuration.aws_api_cloudwatch_alarms_cache_file)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_s3_buckets():
    aws_api.init_s3_buckets()
    aws_api.cache_objects(aws_api.s3_buckets, configuration.aws_api_s3_buckets_cache_file)
    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_all_s3_bucket_objects():
    aws_api.init_s3_buckets(from_cache=True,
                            cache_file=configuration.aws_api_s3_buckets_cache_file)

    aws_api.init_and_cache_all_s3_bucket_objects(configuration.aws_api_s3_bucket_objects_cache_dir)
    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_classic_load_balancers():
    aws_api.init_classic_load_balancers()
    aws_api.cache_objects(aws_api.classic_load_balancers, configuration.aws_api_classic_loadbalancers_cache_file)
    print(f"len(classic_load_balancers) = {len(aws_api.classic_load_balancers)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_load_balancers():
    aws_api.init_load_balancers()
    aws_api.cache_objects(aws_api.load_balancers, configuration.aws_api_loadbalancers_cache_file)
    print(f"len(load_balancers) = {len(aws_api.load_balancers)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_target_groups():
    aws_api.init_target_groups()
    aws_api.cache_objects(aws_api.target_groups, configuration.aws_api_loadbalancer_target_groups_cache_file)
    print(f"len(load_balancers) = {len(aws_api.load_balancers)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ec2_instances():
    aws_api.init_ec2_instances()
    aws_api.cache_objects(aws_api.ec2_instances, configuration.aws_api_ec2_instances_cache_file)
    print(f"len(instances) = {len(aws_api.ec2_instances)}")
    assert isinstance(aws_api.ec2_instances, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_dbs():
    aws_api.init_databases()
    aws_api.cache_objects(aws_api.databases, configuration.aws_api_databases_cache_file)
    print(f"len(databases) = {len(aws_api.databases)}")
    assert isinstance(aws_api.databases, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_hosted_zones():
    aws_api.init_hosted_zones()
    aws_api.cache_objects(aws_api.hosted_zones, configuration.aws_api_hosted_zones_cache_file)
    assert isinstance(aws_api.hosted_zones, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudfront_distributions():
    aws_api.init_cloudfront_distributions()
    aws_api.cache_objects(aws_api.cloudfront_distributions, configuration.aws_api_cloudfront_distributions_cache_file)
    assert isinstance(aws_api.cloudfront_distributions, list)

@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_spot_fleet_requests():
    aws_api.init_spot_fleet_requests()
    aws_api.cache_objects(aws_api.spot_fleet_requests, configuration.aws_api_spot_fleet_requests_cache_file)
    assert isinstance(aws_api.spot_fleet_requests, list)

@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ec2_launch_templates():
    aws_api.init_ec2_launch_templates()
    aws_api.cache_objects(aws_api.ec2_launch_templates, configuration.aws_api_ec2_launch_templates_cache_file)
    assert isinstance(aws_api.ec2_launch_templates, list)
# endregion


if __name__ == "__main__":
    """
    106 = 41.7
    112 = 44 
    """
    test_init_and_cache_raw_large_cloud_watch_log_groups()
