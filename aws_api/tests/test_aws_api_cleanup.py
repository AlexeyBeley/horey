import os
import sys
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "/Users/alexeybe/private/IP/ip")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/base_entities")

from aws_api import AWSAPI
import ignore_me
import logging
logger = logging.Logger(__name__)
from aws_account import AWSAccount

#tested_account = ignore_me.acc_rnd
tested_account = ignore_me.acc_prod_eu

AWSAccount.set_aws_account(tested_account)

aws_api = AWSAPI()

cache_base_path = os.path.join(os.path.expanduser("~"), f"private/aws_api/ignore/cache_objects_{tested_account.name}")
s3_buckets_cache_file = os.path.join(cache_base_path, "s3_buckets.json")
ec2_instances_cache_file = os.path.join(cache_base_path, "ec2_instances.json")
s3_objects_dir = os.path.join(cache_base_path, "s3_buckets_objects")
cloudwatch_log_groups_dir = os.path.join(cache_base_path, "cloudwatch_log_groups")


def test_init_and_cleanup_s3_buckets():
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)
        aws_api.init_s3_buckets(full_information=False)

        aws_api.cleanup_report_s3_buckets()

    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)

buckets_cache_json_file = "/Users/alexeybe/private/aws_api/ignore/cache_objects/s3_buckets.json"
summarised_data_file = "/Users/alexeybe/private/aws_api/ignore/cleanup/us_stg/buckets.json"
bucket_objects_dir = "/Users/alexeybe/private/aws_api/ignore/cache_objects/s3_buckets_objects"


def test_init_from_cache_and_cleanup_s3_buckets():
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)

        aws_api.init_s3_buckets(from_cache=True, cache_file=buckets_cache_json_file)

        aws_api.generate_summarised_s3_cleanup_data(bucket_objects_dir, summarised_data_file)
        aws_api.cleanup_report_s3_buckets_objects(summarised_data_file)


def test_cleanup_report_iam_roles():
    for dict_environ in ignore_me.aws_accounts:
        env = AWSAccount()
        env.init_from_dict(dict_environ)
        AWSAccount.set_aws_account(env)

        aws_api.init_iam_roles(from_cache=True,
                            cache_file="/Users/alexeybe/private/aws_api/ignore/cache_objects/iam_roles.json")

        aws_api.cleanup_report_iam_roles()


lambdas_cache_file = os.path.join(cache_base_path, "lambdas.json")
security_groups_cache_file = os.path.join(cache_base_path, "security_groups.json")


def test_init_from_cache_and_cleanup_lambdas():
        aws_api.init_security_groups(from_cache=True, cache_file=security_groups_cache_file)
        aws_api.init_lambdas(from_cache=True, cache_file=lambdas_cache_file)
        tb_ret = aws_api.cleanup_report_lambdas()
        pdb.set_trace()


iam_policies_cache_file = os.path.join(cache_base_path, "iam_policies.json")

def test_cleanup_report_iam_policies():
    aws_api.init_iam_policies(from_cache=True, cache_file=iam_policies_cache_file)
    aws_api.cleanup_report_iam_policies()


cloud_watch_cache = "cloud_watch_log_groups.json"
cloud_watch_streams = "cloudwatch_log_groups_rnd"


def test_cleanup_report_cloud_watch_logs():
    aws_api.cleanup_report_cloud_watch_log_groups(cloudwatch_log_groups_dir)


hosted_zones_cache_file = os.path.join(cache_base_path, "hosted_zones.json")


def test_prepare_hosted_zones_mapping():
    aws_api.init_hosted_zones(from_cache=True,
                              cache_file=hosted_zones_cache_file)

    aws_api.prepare_hosted_zones_mapping()
    pdb.set_trace()

if __name__ == "__main__":
    #test_init_from_cache_and_cleanup_s3_buckets()
    #test_init_from_cache_and_cleanup_lambdas()
    test_cleanup_report_iam_roles()
    #test_prepare_hosted_zones_mapping()
    #test_cleanup_report_cloud_watch_logs()
