import os
import accounts.ignore_me


class ConfigValues:
    def __init__(self):
        self.account = accounts.ignore_me.acc_default

def main():
    return ConfigValues()

IGNORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore")
CACHE_DIR = os.path.join(IGNORE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

S3_CACHE_DIR = os.path.join(CACHE_DIR, "s3")
os.makedirs(S3_CACHE_DIR, exist_ok=True)
S3_BUCKETS_CACHE_FILE = os.path.join(S3_CACHE_DIR, "s3_buckets.json")

S3_PER_BUCKET_OBJECTS_DIR = os.path.join(S3_CACHE_DIR, "s3_buckets_objects")
os.makedirs(S3_PER_BUCKET_OBJECTS_DIR, exist_ok=True)

CLOUDWATCH_LOG_GROUPS_CACHE_DIR = os.path.join(CACHE_DIR, "cloudwatch_log_groups")
os.makedirs(CLOUDWATCH_LOG_GROUPS_CACHE_DIR, exist_ok=True)
EC2_CACHE_DIR = os.path.join(CACHE_DIR, "ec2")
os.makedirs(EC2_CACHE_DIR, exist_ok=True)
EC2_INSTANCES_CACHE_FILE = os.path.join(EC2_CACHE_DIR, "ec2_instances.json")
SECURITY_GROUPS_CACHE_FILE = os.path.join(EC2_CACHE_DIR, "security_groups.json")

CLOUDWATCH_LOG_GROUPS_CACHE_DIR = os.path.join(CACHE_DIR, "cloudwatch_log_groups")
os.makedirs(CLOUDWATCH_LOG_GROUPS_CACHE_DIR, exist_ok=True)

HOSTED_ZONES_CACHE_FILE = os.path.join(CACHE_DIR, "hosted_zones.json")
LAMBDAS_CACHE_FILE = os.path.join(CACHE_DIR, "lambdas.json")
IAM_POLICIES_CACHE_FILE = os.path.join(CACHE_DIR, "iam_policies.json")

CLEANUP_DIR = os.path.join(IGNORE_DIR, "cleanup")
os.makedirs(CLEANUP_DIR, exist_ok=True)
CLEANUP_LAMBDAS_REPORT = os.path.join(CLEANUP_DIR, "cleanup_lambdas.report")
