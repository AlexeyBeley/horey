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
from environment import Environment

aws_api = AWSAPI()


def test_init_from_cache_ec2instances():
    raise NotImplementedError()
    for dict_environ in ignore_me.environments:
        env = Environment()
        env.init_from_dict(dict_environ)
        Environment.set_environment(env)
        aws_api.init_ec2_instances(from_cache=True, cache_file="/Users/alexeybe/private/aws_api/ignore/cache_objects/ec2_instances.json")

    print(f"len(instances) = {len(aws_api.ec2_instances)}")
    assert isinstance(aws_api.ec2_instances, list)


def test_init_from_cache_s3_buckets():
    aws_api.init_s3_buckets(from_cache=True, cache_file="/Users/alexeybe/private/aws_api/ignore/cache_objects/s3_buckets.json")

    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


if __name__ == "__main__":
    #test_init_and_cache_ec2instances()
    test_init_from_cache_s3_buckets()