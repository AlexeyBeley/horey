"""
Testing AWS Cleaner

"""
import json
import os
import pytest

from horey.aws_cleaner.aws_cleaner import AWSCleaner
from horey.aws_cleaner.aws_cleaner_configuration_policy import (
    AWSCleanerConfigurationPolicy,
)


@pytest.fixture(name="configuration")
def fixture_configuration():
    """
    Fixture used as a base config.

    :return:
    """

    _configuration = AWSCleanerConfigurationPolicy()
    _configuration.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    _configuration.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    _configuration.aws_api_account_name = "cleaner"
    _configuration.managed_accounts_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "aws_managed_accounts.py",
        )
    )
    return _configuration


@pytest.fixture(name="configuration_generate_permissions")
def fixture_configuration_generate_permissions(configuration):
    """
    Set all cleanup_report values to False

    :return:
    """
    for attr in configuration.__dict__:
        if attr.startswith("_cleanup_report_"):
            setattr(configuration, attr, False)
    return configuration


# pylint: disable=missing-function-docstring

@pytest.mark.done
def test_init_aws_cleaner(configuration):
    """
    Test initiation.

    @return:
    """

    assert isinstance(AWSCleaner(configuration), AWSCleaner)


@pytest.mark.done
def test_init_load_balancers(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_load_balancers()
    assert len(cleaner.aws_api.load_balancers) > 1


@pytest.mark.done
def test_init_ec2_volumes(configuration):
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_ec2_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0


@pytest.mark.done
def test_init_target_groups(configuration):
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_target_groups()
    assert len(cleaner.aws_api.target_groups) > 0


@pytest.mark.done
def test_init_ec2_network_interfaces(configuration):
    """
    Test initiation.

    @return:
    """

    cleaner = AWSCleaner(configuration)
    cleaner.init_ec2_network_interfaces()
    assert len(cleaner.aws_api.network_interfaces) > 0


@pytest.mark.done
def test_sub_cleanup_report_ebs_volumes_in_use(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_ebs_volumes_in_use()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_ebs_volumes_sizes(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_ebs_volumes_sizes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_ebs_volumes_types(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_ebs_volumes_types()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_load_balancers(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_load_balancers()
    assert len(cleaner.aws_api.load_balancers) > 0
    assert len(cleaner.aws_api.target_groups) > 0
    assert ret is not None
    assert os.path.exists(configuration.load_balancer_report_file_path)


@pytest.mark.done
def test_cleanup_report_ebs_volumes(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ebs_volumes()
    assert len(cleaner.aws_api.ec2_volumes) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_ebs_report_file_path)


@pytest.mark.done
def test_cleanup_report_acm_certificate(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_acm_certificate()
    assert len(cleaner.aws_api.acm_certificates) > 0
    assert ret is not None
    assert os.path.exists(configuration.acm_certificate_report_file_path)


@pytest.mark.done
def test_cleanup_report_lambdas(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_lambdas()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None
    assert os.path.exists(configuration.lambda_report_file_path)


@pytest.mark.done
def test_cleanup_report_network_interfaces(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_network_interfaces()
    assert len(cleaner.aws_api.network_interfaces) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_interfaces_report_file_path)


@pytest.mark.done
def test_cleanup_report_security_groups(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_security_groups()
    assert len(cleaner.aws_api.security_groups) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_security_groups_report_file_path)


@pytest.mark.done
def test_cleanup_report_ecr_images(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ecr_images()
    assert len(cleaner.aws_api.ecr_images) > 0
    assert ret is not None
    assert os.path.exists(configuration.ec2_security_groups_report_file_path)


@pytest.mark.done
def test_init_cloudwatch_metrics(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_cloudwatch_metrics()
    assert len(cleaner.aws_api.cloud_watch_metrics) > 0


@pytest.mark.done
def test_init_cloudwatch_alarms(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_cloudwatch_alarms()
    assert len(cleaner.aws_api.cloud_watch_alarms) > 0


@pytest.mark.done
def test_init_acm_certificates(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_acm_certificates()
    assert len(cleaner.aws_api.acm_certificates) > 0


@pytest.mark.done
def test_init_hosted_zones(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_hosted_zones()
    assert len(cleaner.aws_api.hosted_zones) > 0


@pytest.mark.done
def test_init_security_groups(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_security_groups()
    assert len(cleaner.aws_api.security_groups) > 1


@pytest.mark.done
def test_init_lambdas(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_lambdas()
    assert len(cleaner.aws_api.lambdas) > 1


@pytest.mark.done
def test_init_cloud_watch_log_groups(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_cloud_watch_log_groups()
    assert len(cleaner.aws_api.cloud_watch_log_groups) > 1
    assert len(cleaner.aws_api.cloud_watch_log_groups_metric_filters) > 1


@pytest.mark.done
def test_init_ecr_images(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_ecr_images()
    assert len(cleaner.aws_api.ecr_images) > 1


@pytest.mark.done
def test_init_dynamodb_tables(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_dynamodb_tables()
    assert len(cleaner.aws_api.dynamodb_tables) > 1


@pytest.mark.done
def test_init_rds(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_rds()
    assert len(cleaner.aws_api.rds_db_clusters) > 0


@pytest.mark.done
def test_init_route_tables(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_route_tables()
    assert len(cleaner.aws_api.route_tables) > 0


@pytest.mark.done
def test_init_subnets(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_subnets()
    assert len(cleaner.aws_api.subnets) > 0


@pytest.mark.skip
def test_init_elasticsearch_domains(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_elasticsearch_domains()
    assert len(cleaner.aws_api.elasticsearch_domains) > 0


@pytest.mark.done
def test_init_elasticache_clusters(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_elasticache_clusters()
    assert len(cleaner.aws_api.elasticache_clusters) > 0


@pytest.mark.todo
def test_init_sqs_queues(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    cleaner.init_sqs_queues()
    assert len(cleaner.aws_api.sqs_queues) > 1


@pytest.mark.done
def test_generate_permissions_cloud_watch_log_groups(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_cloud_watch_log_groups(permissions_only=True)
    for statement in ret:
        if "arn" in str(statement["Resource"]):
            del statement["Resource"]

    assert json.loads(json.dumps(ret)) == [
        {"Sid": "CloudwatchLogs", "Effect": "Allow", "Action": ["logs:DescribeLogGroups", "logs:ListTagsForResource"],
         "Resource": "*"},
        {"Sid": "DescribeMetricFilters", "Effect": "Allow", "Action": "logs:DescribeMetricFilters"}]


@pytest.mark.done
def test_generate_permissions_cloud_watch_metrics(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_cloudwatch_metrics(permissions_only=True)
    for statement in ret:
        if "arn" in str(statement["Resource"]):
            del statement["Resource"]
    assert json.loads(json.dumps(ret)) == [
        {"Sid": "cloudwatchMetrics", "Effect": "Allow", "Action": "cloudwatch:ListMetrics", "Resource": "*"}]


@pytest.mark.done
def test_generate_permissions_cloud_watch_alarms(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_cloudwatch_alarms(permissions_only=True)
    for statement in ret:
        if "arn" in str(statement["Resource"]):
            del statement["Resource"]
    assert json.loads(json.dumps(ret)) == [
        {"Sid": "CloudwatchAlarms", "Effect": "Allow", "Action": "cloudwatch:DescribeAlarms"}]


@pytest.mark.done
def test_generate_permissions_ecr_images(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_ecr_images(permissions_only=True)
    del ret[1]["Resource"]
    assert ret == [{"Sid": "ECRTags", "Effect": "Allow", "Action": "ecr:ListTagsForResource", "Resource": "*"},
                   {"Sid": "GetECR", "Effect": "Allow", "Action": ["ecr:DescribeRepositories", "ecr:DescribeImages"]}]


@pytest.mark.done
def test_generate_permissions_target_groups(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_target_groups(permissions_only=True)
    assert ret == [{
        "Sid": "GetTargetGroups",
        "Effect": "Allow",
        "Action": [
            "elasticloadbalancing:DescribeTargetGroups",
            "elasticloadbalancing:DescribeTargetHealth"
        ],
        "Resource": "*"
    }]


@pytest.mark.done
def test_generate_permissions_init_dynamodb_tables(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_dynamodb_tables(permissions_only=True)
    del ret[1]["Resource"]
    assert ret == [{"Sid": "getDynamodb", "Effect": "Allow", "Action": ["dynamodb:ListTables"], "Resource": "*"},
                   {"Sid": "getDynamodbTable", "Effect": "Allow",
                    "Action": ["dynamodb:DescribeTable", "dynamodb:ListTagsOfResource",
                               "dynamodb:DescribeContinuousBackups"]}]


@pytest.mark.done
def test_generate_permissions_init_rds(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_rds(permissions_only=True)
    del ret[0]["Resource"]
    del ret[1]["Resource"]
    assert ret == [
        {"Sid": "getRDS", "Effect": "Allow", "Action": ["rds:DescribeDBClusters", "rds:ListTagsForResource"]},
        {"Sid": "DescribeDBSubnetGroups", "Effect": "Allow", "Action": ["rds:DescribeDBSubnetGroups"]},
        {"Sid": "DescribeDBEngineVersions", "Effect": "Allow", "Action": ["rds:DescribeDBEngineVersions"],
         "Resource": "*"}]


@pytest.mark.done
def test_generate_permissions_init_route_tables(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_route_tables(permissions_only=True)
    assert ret == [{
        "Sid": "getRouteTables",
        "Effect": "Allow",
        "Action": ["ec2:DescribeRouteTables"],
        "Resource": "*"
    }]


@pytest.mark.done
def test_generate_permissions_init_subnets(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_subnets(permissions_only=True)
    assert ret == [{
        "Sid": "DescribeSubnets",
        "Effect": "Allow",
        "Action": [
            "ec2:DescribeSubnets"
        ],
        "Resource": "*"
    }]


@pytest.mark.done
def test_generate_permissions_init_elasticsearch_domains(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_elasticsearch_domains(permissions_only=True)
    assert ret == [{"Sid": "getElasticsearch", "Effect": "Allow", "Action": ["es:ListDomainNames"], "Resource": "*"}]


@pytest.mark.done
def test_generate_permissions_init_elasticache_clusters(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_elasticache_clusters(permissions_only=True)
    assert ret == [
        {"Sid": "getElasticache", "Effect": "Allow", "Action": ["elasticache:DescribeCacheClusters"], "Resource": "*"}]


@pytest.mark.done
def test_generate_permissions_init_sqs_queues(configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.init_sqs_queues(permissions_only=True)
    del ret[0]["Resource"]
    assert ret == [{"Sid": "getSQS", "Effect": "Allow",
                    "Action": ["sqs:ListQueues", "sqs:GetQueueAttributes", "sqs:ListQueueTags"]}]


@pytest.mark.done
def test_generate_permissions_cleanup_report_load_balancers(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_load_balancers = True
    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert json.loads(json.dumps(ret)) == {"Version": "2012-10-17", "Statement": [
        {"Sid": "LoadBalancers", "Effect": "Allow",
         "Action": ["elasticloadbalancing:DescribeLoadBalancers", "elasticloadbalancing:DescribeListeners",
                    "elasticloadbalancing:DescribeRules", "elasticloadbalancing:DescribeTags"], "Resource": "*"},
        {"Sid": "GetTargetGroups", "Effect": "Allow",
         "Action": ["elasticloadbalancing:DescribeTargetGroups", "elasticloadbalancing:DescribeTargetHealth"],
         "Resource": "*"},
        {"Sid": "getRouteTables", "Effect": "Allow", "Action": ["ec2:DescribeRouteTables"], "Resource": "*"},
        {"Sid": "DescribeSubnets", "Effect": "Allow", "Action": ["ec2:DescribeSubnets"], "Resource": "*"}]}


@pytest.mark.done
def test_generate_permissions_cleanup_report_ebs_volumes(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_ebs_volumes = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert ret == {"Version": "2012-10-17", "Statement": [
        {"Sid": "DescribeVolumes", "Effect": "Allow", "Action": "ec2:DescribeVolumes", "Resource": "*"}]}


@pytest.mark.done
def test_generate_permissions_cleanup_report_route53_certificates(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_route53_certificates = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    expected = [
        {"Sid": "Route53", "Effect": "Allow", "Action": ["route53:ListHostedZones", "route53:ListResourceRecordSets"],
         "Resource": "*"},
        {"Sid": "ListCertificates", "Effect": "Allow", "Action": "acm:ListCertificates", "Resource": "*"},
        {"Sid": "SpecificCertificate", "Effect": "Allow",
         "Action": ["acm:DescribeCertificate", "acm:ListTagsForCertificate"]}]
    for statement in ret["Statement"]:
        if "arn" in str(statement["Resource"]):
            del statement["Resource"]
        assert statement in expected
    assert len(expected) == len(ret["Statement"])

@pytest.mark.done
def test_generate_permissions_cleanup_report_route53_loadbalancers(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_route53_loadbalancers = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert ret["Statement"] == [
        {"Sid": "Route53", "Effect": "Allow", "Action": ["route53:ListHostedZones", "route53:ListResourceRecordSets"],
         "Resource": "*"},
        {"Sid": "LoadBalancers", "Effect": "Allow",
         "Action": ["elasticloadbalancing:DescribeLoadBalancers",
                    "elasticloadbalancing:DescribeListeners", "elasticloadbalancing:DescribeRules",
                    "elasticloadbalancing:DescribeTags"], "Resource": "*"}]


@pytest.mark.done
def test_generate_permissions_cleanup_report_lambdas(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_lambdas = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    expected = [{"Sid": "GetFunctions", "Effect": "Allow",
                 "Action": ["lambda:ListFunctions", "lambda:GetFunctionConcurrency"], "Resource": "*"},
                {"Sid": "LambdaGetPolicy", "Effect": "Allow", "Action": "lambda:GetPolicy"},
                {"Sid": "DescribeSecurityGroups", "Effect": "Allow", "Action": "ec2:DescribeSecurityGroups",
                 "Resource": "*"},
                {"Sid": "CloudwatchLogs", "Effect": "Allow", "Action": ["logs:DescribeLogGroups", "logs:ListTagsForResource"], "Resource": "*"},
                {"Action": "logs:DescribeMetricFilters", "Effect": "Allow", "Sid": "DescribeMetricFilters"}
                ]

    ret = cleaner.generate_permissions()

    for statement in ret["Statement"]:
        if "arn" in str(statement["Resource"]):
            del statement["Resource"]
        assert statement in expected
    assert len(expected) == len(ret["Statement"])


@pytest.mark.done
def test_generate_permissions_cleanup_report_ec2_instances(
        configuration_generate_permissions: AWSCleanerConfigurationPolicy):
    configuration_generate_permissions.cleanup_report_ec2_instances = True

    cleaner = AWSCleaner(configuration_generate_permissions)
    ret = cleaner.generate_permissions()
    assert ret["Statement"] == [
        {"Sid": "DescribeImages", "Effect": "Allow", "Action": "ec2:DescribeImages", "Resource": "*"},
        {"Sid": "DescribeInstances", "Effect": "Allow", "Action": "ec2:DescribeInstances", "Resource": "*"}]


@pytest.mark.done
def test_sub_cleanup_report_lambdas_large_size(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_large_size()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_lambdas_not_running(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_not_running()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_lambdas_deprecate(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_deprecate()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_lambdas_security_group(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_security_group()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_report_lambdas_old_code(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_lambdas_old_code()
    assert len(cleaner.aws_api.lambdas) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_ec2_instances(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_ec2_instances()
    assert len(cleaner.aws_api.ec2_instances) > 0
    assert ret is not None


@pytest.mark.done
def test_cleanup_report_dynamodb(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_dynamodb()
    assert len(cleaner.aws_api.dynamodb_tables) > 0
    assert ret is not None
    assert os.path.exists(cleaner.configuration.dynamodb_report_file_path)


@pytest.mark.done
def test_cleanup_report_rds(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_rds()
    assert len(cleaner.aws_api.rds_db_clusters) > 0
    assert ret is not None
    assert os.path.exists(cleaner.configuration.rds_report_file_path)


@pytest.mark.todo
def test_cleanup_opensearch(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_opensearch()
    assert len(cleaner.aws_api.elasticsearch_domains) > 0
    assert ret is not None
    assert os.path.exists(cleaner.configuration.elasticsearch_domains_report_file_path)


@pytest.mark.done
def test_cleanup_report_elasticache(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_elasticache()
    assert len(cleaner.aws_api.elasticache_clusters) > 0
    assert ret is not None
    assert os.path.exists(cleaner.configuration.elasticache_report_file_path)


@pytest.mark.done
def test_cleanup_report_cloudwatch(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_cloudwatch()
    assert len(cleaner.aws_api.cloud_watch_log_groups) > 0
    assert ret is not None
    assert os.path.exists(cleaner.configuration.cloud_watch_report_file_path)


@pytest.mark.done
def test_cleanup_report_sqs(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.cleanup_report_sqs()
    assert len(cleaner.aws_api.sqs_queues) > 0
    assert ret is not None
    assert os.path.exists(cleaner.configuration.sqs_report_file_path)


@pytest.mark.todo
def test_clean(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.clean()
    assert len(cleaner.aws_api.ec2_instances) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_loadbalancer_has_no_metrics(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_loadbalancer_has_no_metrics()
    assert len(cleaner.aws_api.load_balancers) > 0
    assert ret is not None


@pytest.mark.done
def test_sub_cleanup_target_groups(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_target_groups()
    assert len(cleaner.aws_api.target_groups) > 0
    assert ret is not None


@pytest.mark.wip
def test_sub_cleanup_report_rds_cluster_monitoring(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_rds_cluster_monitoring()
    assert len(cleaner.aws_api.rds_db_clusters) > 0
    assert ret is not None

@pytest.mark.wip
def test_sub_cleanup_report_rds_instance_monitoring(configuration):
    cleaner = AWSCleaner(configuration)
    ret = cleaner.sub_cleanup_report_rds_instance_monitoring()
    assert len(cleaner.aws_api.rds_db_instances) > 0
    assert ret is not None

@pytest.mark.done
def test_generate_permissions_all(
        configuration: AWSCleanerConfigurationPolicy):
    cleaner = AWSCleaner(configuration)
    expected_sids = {"ListCertificates", "ECRTags", "GetFunctions", "DescribeSubnets", "DescribeNetworkInterfaces",
                     "getSQS", "DescribeMetricFilters", "getRouteTables", "CloudwatchLogs", "SpecificCertificate",
                     "getRDS", "DescribeImages", "getDynamodb", "DescribeDBEngineVersions", "DescribeInstances",
                     "DescribeDBSubnetGroups", "getElasticache", "DescribeSecurityGroups", "Route53", "LoadBalancers",
                     "CloudwatchAlarms", "getDynamodbTable", "GetECR", "GetTargetGroups", "DescribeVolumes",
                     "LambdaGetPolicy"}

    ret = cleaner.generate_permissions()
    sids = {statement["Sid"] for statement in ret["Statement"]}
    assert sids == expected_sids
    assert len(ret["Statement"]) == len(expected_sids)
    assert os.path.exists(cleaner.configuration.permissions_file_path)


@pytest.mark.done
def test_cleanup_reports_in_aws_cleaner_match_configuration_policy_cleanup_reports():
    """

    :return:
    """
    config_cleanup_report_attrs = [attr_name for attr_name in AWSCleanerConfigurationPolicy.__dict__ if
                                   attr_name.startswith("cleanup_report_")]
    cleaner_cleanup_report_attrs = [attr_name for attr_name in AWSCleaner.__dict__ if
                                    attr_name.startswith("cleanup_report_")]

    assert set(config_cleanup_report_attrs) == set(cleaner_cleanup_report_attrs)
    for x in cleaner_cleanup_report_attrs:
        if x not in config_cleanup_report_attrs:
            print(f"""\n        self._{x} = None

    @property
    def {x}(self):
        if self._{x} is None:
            self._{x} = True
        return self._{x}

    @{x}.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def {x}(self, value):
        self._{x} = value
    """)
