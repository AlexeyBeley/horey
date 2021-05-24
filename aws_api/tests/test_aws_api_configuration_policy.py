import os


from horey.h_logger import get_logger
logger = get_logger()
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy

#@pytest.mark.skip(reason="No way of currently testing this")
def test_init_aws_api_configuration_policy():
    configuration = AWSAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_values.py")
    configuration.init_from_file()

    assert configuration.aws_api_s3_cache_dir == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/s3")
    assert configuration.aws_api_s3_buckets_cache_file == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/s3/buckets.json")

    assert configuration.aws_api_ec2_cache_dir == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/ec2")
    assert configuration.aws_api_ec2_security_groups_cache_file == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/ec2/network_security_groups.json")

    assert configuration.aws_api_lambda_cache_dir == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/lambda")
    assert configuration.aws_api_lambdas_cache_file == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/lambda/lambdas.json")

    assert configuration.aws_api_cleanup_reports_dir == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/cleanup")
    assert configuration.aws_api_cleanups_lambda_file == os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore/cache/12345678910/cleanup/lambda.txt")
