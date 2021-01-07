import os
import sys
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "/Users/alexeybe/private/IP/ip")
sys.path.insert(0, "~/private/aws_api/ignore")
sys.path.insert(0, "~/private/aws_api/src/base_entities")

from aws_api import AWSAPI
import ignore_me
from h_logger import get_logger
from aws_account import AWSAccount

logger = get_logger()
# Set account here:
tested_account = ignore_me.acc_prod_eu
AWSAccount.set_aws_account(tested_account)

aws_api = AWSAPI()

cache_base_path = os.path.join(os.path.expanduser("~"), f"private/aws_api/ignore/cache_objects_{tested_account.name}")
s3_buckets_cache_file = os.path.join(cache_base_path, "s3_buckets.json")
ec2_instances_cache_file = os.path.join(cache_base_path, "ec2_instances.json")
lambdas_cache_file = os.path.join(cache_base_path, "lambdas.json")
iam_policies_cache_file = os.path.join(cache_base_path, "iam_policies.json")
iam_roles_cache_file = os.path.join(cache_base_path, "iam_roles.json")
cloudwatch_logs_cache_file = os.path.join(cache_base_path, "cloudwatch_logs.json")
classic_load_balancers_cache_file = os.path.join(cache_base_path, "classic_load_balancers.json")
security_groups_cache_file = os.path.join(cache_base_path, "security_groups.json")
hosted_zones_cache_file = os.path.join(cache_base_path, "hosted_zones.json")
load_balancers_cache_file = os.path.join(cache_base_path, "load_balancers.json")

s3_objects_dir = os.path.join(cache_base_path, "s3_buckets_objects")
cloudwatch_log_groups_dir = os.path.join(cache_base_path, "cloudwatch_log_groups")


def test_init_and_cache_ec2instances():
    aws_api.init_ec2_instances()
    aws_api.cache_objects(aws_api.ec2_instances, ec2_instances_cache_file)
    print(f"len(instances) = {len(aws_api.ec2_instances)}")
    assert isinstance(aws_api.ec2_instances, list)


def test_init_and_cache_s3_buckets():
    aws_api.init_s3_buckets()
    aws_api.cache_objects(aws_api.s3_buckets, s3_buckets_cache_file)
    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


def test_init_and_cache_s3_bucket_objects():
    aws_api.init_s3_buckets(from_cache=True,
                            cache_file=s3_buckets_cache_file)

    aws_api.init_and_cache_s3_bucket_objects(s3_objects_dir)

    pdb.set_trace()

    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


def test_init_and_cache_raw_large_cloud_watch_log_groups():
    aws_api.init_and_cache_raw_large_cloud_watch_log_groups(cloudwatch_log_groups_dir)
    print(f"len(cloud_watch_log_groups) = {len(aws_api.cloud_watch_log_groups)}")
    assert isinstance(aws_api.cloud_watch_log_groups, list)


def test_init_and_cache_lambdas():
    aws_api.init_lambdas()
    aws_api.cache_objects(aws_api.lambdas, lambdas_cache_file)
    logger.info(f"len(lambdas) = {len(aws_api.lambdas)}")
    assert isinstance(aws_api.lambdas, list)


def test_init_and_cache_iam_roles():
    aws_api.init_iam_policies(from_cache=True, cache_file=iam_policies_cache_file)
    aws_api.init_iam_roles()
    aws_api.cache_objects(aws_api.iam_roles, iam_roles_cache_file)

    print(f"len(iam_roles) = {len(aws_api.iam_roles)}")
    assert isinstance(aws_api.iam_roles, list)


def test_init_and_cache_iam_policies():
    aws_api.init_iam_policies()
    aws_api.cache_objects(aws_api.iam_policies, iam_policies_cache_file)

    logger.info(f"len(iam_policies) = {len(aws_api.iam_policies)}")
    assert isinstance(aws_api.iam_policies, list)


def test_init_and_cache_cloudwatch_logs():
    aws_api.init_cloud_watch_log_groups()
    aws_api.cache_objects(aws_api.cloud_watch_log_groups, cloudwatch_logs_cache_file)

    print(f"len(cloud_watch_log_groups) = {len(aws_api.cloud_watch_log_groups)}")
    assert isinstance(aws_api.cloud_watch_log_groups, list)


def test_init_and_cache_hosted_zones():
    aws_api.init_hosted_zones()
    aws_api.cache_objects(aws_api.hosted_zones, hosted_zones_cache_file)

    assert isinstance(aws_api.iam_roles, list)


def test_init_and_cache_classic_load_balancers():
    aws_api.init_classic_load_balancers()
    aws_api.cache_objects(aws_api.classic_load_balancers, classic_load_balancers_cache_file)
    print(f"len(classic_load_balancers) = {len(aws_api.classic_load_balancers)}")


def test_init_and_cache_load_balancers():
    aws_api.init_load_balancers()
    aws_api.cache_objects(aws_api.load_balancers, load_balancers_cache_file)
    print(f"len(load_balancers) = {len(aws_api.load_balancers)}")


def test_init_and_cache_security_groups():
    aws_api.init_security_groups()
    aws_api.cache_objects(aws_api.security_groups, security_groups_cache_file)
    print(f"len(security_groups) = {len(aws_api.security_groups)}")


if __name__ == "__main__":
    test_init_and_cache_ec2instances()
    #test_init_and_cache_s3_buckets()
    #test_init_and_cache_lambdas()
    #test_init_and_cache_iam_policies()
    #test_init_and_cache_iam_roles()
    #test_init_and_cache_hosted_zones()
    #test_init_and_cache_classic_load_balancers()
    #test_init_and_cache_load_balancers()
    #test_init_and_cache_security_groups()
    #test_init_and_cache_s3_bucket_objects()
    #test_init_and_cache_raw_large_cloud_watch_log_groups()
    #test_init_and_cache_cloudwatch_logs()
