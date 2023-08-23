"""
Init and cache AWS objects.

"""

import os
import json

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.base_entities.region import Region


# Uncomment next line to save error lines to /tmp/error.log
configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)

logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "aws_api_configuration_values_all_access.py",
    )
)
configuration.init_from_file()

aws_api = AWSAPI(configuration=configuration)

# pylint: disable= missing-function-docstring

# region done
@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_and_cache_iam_policies():
    aws_api.init_iam_policies()
    aws_api.cache_objects(
        aws_api.iam_policies, configuration.aws_api_iam_policies_cache_file
    )
    logger.info(f"len(iam_policies) = {len(aws_api.iam_policies)}")
    assert isinstance(aws_api.iam_policies, list)


@pytest.mark.skip(reason="IAM roles will be inited explicitly")
def test_init_and_cache_iam_roles():
    aws_api.init_iam_policies(
        from_cache=True, cache_file=configuration.aws_api_iam_policies_cache_file
    )
    aws_api.init_iam_roles()
    aws_api.cache_objects(aws_api.iam_roles, configuration.aws_api_iam_roles_cache_file)

    print(f"len(iam_roles) = {len(aws_api.iam_roles)}")
    assert isinstance(aws_api.iam_roles, list)


@pytest.mark.skip(reason="IAM roles will be inited explicitly")
def test_init_and_cache_iam_instance_profiles():
    aws_api.init_iam_policies(
        from_cache=True, cache_file=configuration.aws_api_iam_policies_cache_file
    )
    aws_api.init_iam_instance_profiles()
    aws_api.cache_objects(
        aws_api.iam_instance_profiles,
        configuration.aws_api_iam_instance_profiles_cache_file,
    )

    print(f"len(iam_instance_profiles) = {len(aws_api.iam_instance_profiles)}")
    assert isinstance(aws_api.iam_instance_profiles, list)


@pytest.mark.skip(reason="IAM roles will be inited explicitly")
def test_init_and_cache_iam_groups():
    aws_api.init_iam_groups()
    aws_api.cache_objects(
        aws_api.iam_groups, configuration.aws_api_iam_groups_cache_file
    )

    print(f"len(iam_groups) = {len(aws_api.iam_groups)}")
    assert isinstance(aws_api.iam_groups, list)


@pytest.mark.skip(reason="IAM roles will be inited explicitly")
def test_init_and_cache_iam_users():
    aws_api.init_iam_users()
    aws_api.cache_objects(aws_api.users, configuration.aws_api_iam_users_cache_file)
    print(f"len(users) = {len(aws_api.users)}")
    assert isinstance(aws_api.users, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_network_interfaces():
    aws_api.init_network_interfaces()
    aws_api.cache_objects(
        aws_api.network_interfaces,
        configuration.aws_api_ec2_network_interfaces_cache_file,
    )
    logger.info(f"len(network_interfaces) = {len(aws_api.network_interfaces)}")
    assert len(aws_api.network_interfaces) > 0


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_security_all_groups():
    aws_api.init_security_groups()
    aws_api.cache_objects(
        aws_api.security_groups, configuration.aws_api_ec2_security_groups_cache_file
    )
    logger.info(f"len(security_groups) = {len(aws_api.security_groups)}")
    assert len(aws_api.security_groups) > 0


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_security_regions_groups():
    ret = []
    for region_mark in ["us-east-1", "eu-central-1"]:
        ret += aws_api.ec2_client.get_region_security_groups(Region.get_region(region_mark))
    aws_api.cache_objects(
        ret, configuration.aws_api_ec2_security_groups_cache_file
    )
    logger.info(f"len(security_groups) = {len(aws_api.security_groups)}")
    assert len(ret) > 0


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_lambdas():
    aws_api.init_lambdas()
    aws_api.cache_objects(aws_api.lambdas, configuration.aws_api_lambdas_cache_file)
    logger.info(f"len(lambdas) = {len(aws_api.lambdas)}")
    assert isinstance(aws_api.lambdas, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_raw_large_cloud_watch_log_groups():
    "4470"
    aws_api.init_and_cache_raw_large_cloud_watch_log_groups(
        configuration.aws_api_cloudwatch_log_groups_streams_cache_dir
    )
    print(f"len(cloud_watch_log_groups) = {len(aws_api.cloud_watch_log_groups)}")
    assert isinstance(aws_api.cloud_watch_log_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudwatch_logs():
    aws_api.init_cloud_watch_log_groups()
    aws_api.cache_objects(
        aws_api.cloud_watch_log_groups,
        configuration.aws_api_cloudwatch_log_groups_cache_file,
    )
    print(f"len(cloud_watch_log_groups) = {len(aws_api.cloud_watch_log_groups)}")
    assert isinstance(aws_api.cloud_watch_log_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudwatch_log_groups_metric_filters():
    aws_api.init_cloud_watch_log_groups_metric_filters()
    aws_api.cache_objects(
        aws_api.cloud_watch_log_groups_metric_filters,
        configuration.aws_api_cloudwatch_log_groups_metric_filters_cache_file,
    )
    print(
        f"len(cloud_watch_log_group_metric_filters) = {len(aws_api.cloud_watch_log_groups_metric_filters)}"
    )
    assert isinstance(aws_api.cloud_watch_log_groups_metric_filters, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_dynamodb_tables():
    aws_api.init_dynamodb_tables()
    aws_api.cache_objects(
        aws_api.dynamodb_tables, configuration.aws_api_dynamodb_tables_cache_file
    )
    print(f"len(dynamodb_tables) = {len(aws_api.dynamodb_tables)}")
    assert isinstance(aws_api.dynamodb_tables, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_dynamodb_endpoints():
    aws_api.init_dynamodb_endpoints()
    aws_api.cache_objects(
        aws_api.dynamodb_endpoints, configuration.aws_api_dynamodb_endpoints_cache_file
    )
    print(f"len(dynamodb_endpoints) = {len(aws_api.dynamodb_endpoints)}")
    assert isinstance(aws_api.dynamodb_endpoints, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_sesv2_email_identities():
    aws_api.init_sesv2_email_identities()
    aws_api.cache_objects(
        aws_api.sesv2_email_identities,
        configuration.aws_api_sesv2_email_identities_cache_file,
    )
    print(f"len(sesv2_email_identities) = {len(aws_api.sesv2_email_identities)}")
    assert isinstance(aws_api.sesv2_email_identities, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_sesv2_email_templates():
    aws_api.init_sesv2_email_templates()
    aws_api.cache_objects(
        aws_api.sesv2_email_templates,
        configuration.aws_api_sesv2_email_templates_cache_file,
    )
    print(f"len(sesv2_email_templates) = {len(aws_api.sesv2_email_templates)}")
    assert isinstance(aws_api.sesv2_email_templates, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_sesv2_configuration_sets():
    aws_api.init_sesv2_configuration_sets(full_information=True)
    aws_api.cache_objects(
        aws_api.sesv2_configuration_sets,
        configuration.aws_api_sesv2_configuration_sets_cache_file,
    )
    print(f"len(sesv2_configuration_sets) = {len(aws_api.sesv2_configuration_sets)}")
    assert isinstance(aws_api.sesv2_configuration_sets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_sns_topics():
    aws_api.init_sns_topics()
    aws_api.cache_objects(
        aws_api.sns_topics, configuration.aws_api_sns_topics_cache_file
    )
    print(f"len(sns_topics) = {len(aws_api.sns_topics)}")
    assert isinstance(aws_api.sns_topics, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_sns_subscriptions():
    aws_api.init_sns_subscriptions()
    aws_api.cache_objects(
        aws_api.sns_subscriptions, configuration.aws_api_sns_subscriptions_cache_file
    )
    print(f"len(sns_subscriptions) = {len(aws_api.sns_subscriptions)}")
    assert isinstance(aws_api.sns_subscriptions, list)


@pytest.mark.skip(reason="No way of currently testing cloudwatch metrics")
def test_init_and_cache_cloudwatch_metrics():
    aws_api.cache_raw_cloud_watch_metrics(
        configuration.aws_api_cloudwatch_metrics_cache_dir
    )


@pytest.mark.skip(reason="No way of currently testing cloudwatch metrics")
def test_init_and_cache_cloudwatch_alarms():
    aws_api.init_cloud_watch_alarms()
    aws_api.cache_objects(
        aws_api.cloud_watch_alarms,
        configuration.aws_api_cloudwatch_alarms_cache_file,
        indent=4,
    )


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_s3_buckets():
    aws_api.init_s3_buckets()
    aws_api.cache_objects(
        aws_api.s3_buckets, configuration.aws_api_s3_buckets_cache_file
    )
    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_all_s3_bucket_objects():
    aws_api.init_s3_buckets(
        from_cache=True, cache_file=configuration.aws_api_s3_buckets_cache_file
    )

    aws_api.init_and_cache_all_s3_bucket_objects(
        configuration.aws_api_s3_bucket_objects_cache_dir
    )
    print(f"len(s3_buckets) = {len(aws_api.s3_buckets)}")
    assert isinstance(aws_api.s3_buckets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_classic_load_balancers():
    aws_api.init_classic_load_balancers()
    aws_api.cache_objects(
        aws_api.classic_load_balancers,
        configuration.aws_api_classic_loadbalancers_cache_file,
    )
    print(f"len(classic_load_balancers) = {len(aws_api.classic_load_balancers)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_load_balancers():
    aws_api.init_load_balancers()
    aws_api.cache_objects(
        aws_api.load_balancers, configuration.aws_api_loadbalancers_cache_file
    )
    print(f"len(load_balancers) = {len(aws_api.load_balancers)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_target_groups():
    aws_api.init_target_groups()
    aws_api.cache_objects(
        aws_api.target_groups,
        configuration.aws_api_loadbalancer_target_groups_cache_file,
    )
    print(f"len(target_groups) = {len(aws_api.target_groups)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ec2_instances():
    aws_api.init_ec2_instances()
    aws_api.cache_objects(
        aws_api.ec2_instances, configuration.aws_api_ec2_instances_cache_file
    )
    print(f"len(instances) = {len(aws_api.ec2_instances)}")
    assert isinstance(aws_api.ec2_instances, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_rds_db_instances():
    aws_api.init_rds_db_instances()
    aws_api.cache_objects(
        aws_api.rds_db_instances, configuration.aws_api_rds_db_instances_cache_file
    )
    print(f"len(rds_db_instances) = {len(aws_api.rds_db_instances)}")
    assert isinstance(aws_api.rds_db_instances, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_rds_db_clusters():
    aws_api.init_rds_db_clusters()
    aws_api.cache_objects(
        aws_api.rds_db_clusters, configuration.aws_api_rds_db_clusters_cache_file
    )
    print(f"len(rds_db_clusters) = {len(aws_api.rds_db_clusters)}")
    assert isinstance(aws_api.rds_db_clusters, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elasticache_clusters():
    aws_api.init_elasticache_clusters()
    aws_api.cache_objects(
        aws_api.elasticache_clusters,
        configuration.aws_api_elasticache_clusters_cache_file,
    )
    print(f"len(elasticache_clusters) = {len(aws_api.elasticache_clusters)}")
    assert isinstance(aws_api.elasticache_clusters, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elasticache_replication_groups():
    aws_api.init_elasticache_replication_groups()
    aws_api.cache_objects(
        aws_api.elasticache_replication_groups,
        configuration.aws_api_elasticache_replication_groups_cache_file,
    )
    print(
        f"len(elasticache_replication_groups) = {len(aws_api.elasticache_replication_groups)}"
    )
    assert isinstance(aws_api.elasticache_replication_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elasticache_cache_parameter_groups():
    aws_api.init_elasticache_cache_parameter_groups()
    aws_api.cache_objects(
        aws_api.elasticache_cache_parameter_groups,
        configuration.aws_api_elasticache_cache_parameter_groups_cache_file,
    )
    print(
        f"len(elasticache_cache_parameter_groups) = {len(aws_api.elasticache_cache_parameter_groups)}"
    )
    assert isinstance(aws_api.elasticache_cache_parameter_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elasticache_cache_subnet_groups():
    aws_api.init_elasticache_cache_subnet_groups()
    aws_api.cache_objects(
        aws_api.elasticache_cache_subnet_groups,
        configuration.aws_api_elasticache_cache_subnet_groups_cache_file,
    )
    print(
        f"len(elasticache_cache_subnet_groups) = {len(aws_api.elasticache_cache_subnet_groups)}"
    )
    assert isinstance(aws_api.elasticache_cache_subnet_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elasticache_cache_security_groups():
    aws_api.init_elasticache_cache_security_groups()
    aws_api.cache_objects(
        aws_api.elasticache_cache_security_groups,
        configuration.aws_api_elasticache_cache_security_groups_cache_file,
    )
    print(
        f"len(elasticache_cache_security_groups) = {len(aws_api.elasticache_cache_security_groups)}"
    )
    assert isinstance(aws_api.elasticache_cache_security_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_rds_db_subnet_groups():
    aws_api.init_rds_db_subnet_groups()
    aws_api.cache_objects(
        aws_api.rds_db_subnet_groups,
        configuration.aws_api_rds_db_subnet_groups_cache_file,
    )
    print(f"len(rds_db_subnet_groups) = {len(aws_api.rds_db_subnet_groups)}")
    assert isinstance(aws_api.rds_db_subnet_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_rds_db_cluster_parameter_groups():
    aws_api.init_rds_db_cluster_parameter_groups()
    aws_api.cache_objects(
        aws_api.rds_db_cluster_parameter_groups,
        configuration.aws_api_rds_db_cluster_parameter_groups_cache_file,
    )
    print(
        f"len(rds_db_cluster_parameter_groups) = {len(aws_api.rds_db_cluster_parameter_groups)}"
    )
    assert isinstance(aws_api.rds_db_cluster_parameter_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_rds_db_cluster_snapshots():
    aws_api.init_rds_db_cluster_snapshots()
    aws_api.cache_objects(
        aws_api.rds_db_cluster_snapshots,
        configuration.aws_api_rds_db_cluster_snapshots_cache_file,
    )
    print(f"len(rds_db_cluster_snapshots) = {len(aws_api.rds_db_cluster_snapshots)}")
    assert isinstance(aws_api.rds_db_cluster_snapshots, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_rds_db_parameter_groups():
    aws_api.init_rds_db_parameter_groups()
    aws_api.cache_objects(
        aws_api.rds_db_parameter_groups,
        configuration.aws_api_rds_db_parameter_groups_cache_file,
    )
    print(f"len(rds_db_parameter_groups) = {len(aws_api.rds_db_parameter_groups)}")
    assert isinstance(aws_api.rds_db_parameter_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_hosted_zones():
    aws_api.init_hosted_zones()
    aws_api.cache_objects(
        aws_api.hosted_zones, configuration.aws_api_hosted_zones_cache_file
    )
    assert isinstance(aws_api.hosted_zones, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudfront_distributions():
    aws_api.init_cloudfront_distributions()
    aws_api.cache_objects(
        aws_api.cloudfront_distributions,
        configuration.aws_api_cloudfront_distributions_cache_file,
    )
    assert isinstance(aws_api.cloudfront_distributions, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_cloudfront_origin_access_identities():
    aws_api.init_cloudfront_origin_access_identities()
    aws_api.cache_objects(
        aws_api.cloudfront_origin_access_identities,
        configuration.aws_api_cloudfront_origin_access_identities_cache_file,
    )
    assert isinstance(aws_api.cloudfront_origin_access_identities, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_spot_fleet_requests():
    aws_api.init_spot_fleet_requests()
    aws_api.cache_objects(
        aws_api.spot_fleet_requests,
        configuration.aws_api_spot_fleet_requests_cache_file,
    )
    assert isinstance(aws_api.spot_fleet_requests, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ec2_launch_templates():
    aws_api.init_ec2_launch_templates()
    aws_api.cache_objects(
        aws_api.ec2_launch_templates,
        configuration.aws_api_ec2_launch_templates_cache_file,
    )
    assert isinstance(aws_api.ec2_launch_templates, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ec2_launch_template_versions():
    aws_api.init_ec2_launch_templates()
    aws_api.init_ec2_launch_template_versions()
    aws_api.cache_objects(
        aws_api.ec2_launch_template_versions,
        configuration.aws_api_ec2_launch_template_versions_cache_file,
    )
    assert isinstance(aws_api.ec2_launch_template_versions, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_event_bridge_rules():
    aws_api.init_event_bridge_rules()
    aws_api.cache_objects(
        aws_api.event_bridge_rules, configuration.aws_api_event_bridge_rules_cache_file
    )
    assert isinstance(aws_api.event_bridge_rules, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_secrets_manager_secrets():
    aws_api.init_secrets_manager_secrets()
    assert isinstance(aws_api.secrets_manager_secrets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_servicediscovery_services():
    aws_api.init_servicediscovery_services()
    aws_api.cache_objects(
        aws_api.servicediscovery_services,
        configuration.aws_api_servicediscovery_services_cache_file,
    )
    assert isinstance(aws_api.servicediscovery_services, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_servicediscovery_namespaces():
    aws_api.init_servicediscovery_namespaces()
    aws_api.cache_objects(
        aws_api.servicediscovery_namespaces,
        configuration.aws_api_servicediscovery_namespaces_cache_file,
    )
    assert isinstance(aws_api.servicediscovery_namespaces, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elasticsearch_domains():
    aws_api.init_elasticsearch_domains()
    aws_api.cache_objects(
        aws_api.elasticsearch_domains,
        configuration.aws_api_elasticsearch_domains_cache_file,
    )
    assert isinstance(aws_api.elasticsearch_domains, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_managed_prefix_lists():
    aws_api.init_managed_prefix_lists()
    aws_api.cache_objects(
        aws_api.managed_prefix_lists,
        configuration.aws_api_managed_prefix_lists_cache_file,
    )
    assert isinstance(aws_api.managed_prefix_lists, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_vpcs():
    all_regions = list(aws_api.aws_accounts.values())[0].regions
    aws_api.init_vpcs(region=all_regions)
    aws_api.cache_objects(aws_api.vpcs, configuration.aws_api_vpcs_cache_file)
    assert isinstance(aws_api.vpcs, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_subnets():
    all_regions = list(list(aws_api.aws_accounts.values())[0].regions.values())
    aws_api.init_subnets(region=all_regions)
    aws_api.cache_objects(aws_api.subnets, configuration.aws_api_subnets_cache_file)
    assert isinstance(aws_api.subnets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_glue_tables():
    all_regions = list(list(aws_api.aws_accounts.values())[0].regions.values())
    aws_api.init_glue_tables(region=all_regions)
    aws_api.cache_objects(
        aws_api.glue_tables, configuration.aws_api_glue_tables_cache_file
    )
    assert isinstance(aws_api.glue_tables, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_glue_databases():
    all_regions = list(list(aws_api.aws_accounts.values())[0].regions.values())
    aws_api.init_glue_databases(region=all_regions)
    aws_api.cache_objects(
        aws_api.glue_databases, configuration.aws_api_glue_databases_cache_file
    )
    assert isinstance(aws_api.glue_databases, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_availability_zones():
    aws_api.init_availability_zones()
    aws_api.cache_objects(
        aws_api.availability_zones, configuration.aws_api_availability_zones_cache_file
    )
    assert isinstance(aws_api.availability_zones, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_amis():
    aws_api.init_amis()
    aws_api.cache_objects(aws_api.amis, configuration.aws_api_amis_cache_file)
    assert isinstance(aws_api.amis, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_key_pairs():
    aws_api.init_key_pairs()
    aws_api.cache_objects(aws_api.key_pairs, configuration.aws_api_key_pairs_cache_file)
    assert isinstance(aws_api.key_pairs, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_internet_gateways():
    aws_api.init_internet_gateways()
    aws_api.cache_objects(
        aws_api.internet_gateways, configuration.aws_api_internet_gateways_cache_file
    )
    assert isinstance(aws_api.internet_gateways, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_vpc_peerings():
    aws_api.init_vpc_peerings()
    aws_api.cache_objects(
        aws_api.vpc_peerings, configuration.aws_api_vpc_peerings_cache_file
    )
    assert isinstance(aws_api.vpc_peerings, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_route_tables():
    aws_api.init_route_tables()
    aws_api.cache_objects(
        aws_api.route_tables, configuration.aws_api_route_tables_cache_file
    )
    assert isinstance(aws_api.route_tables, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_elastic_addresses():
    aws_api.init_elastic_addresses()
    aws_api.cache_objects(
        aws_api.elastic_addresses, configuration.aws_api_elastic_addresses_cache_file
    )
    assert isinstance(aws_api.elastic_addresses, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_nat_gateways():
    aws_api.init_nat_gateways()
    aws_api.cache_objects(
        aws_api.nat_gateways, configuration.aws_api_nat_gateways_cache_file
    )
    assert isinstance(aws_api.nat_gateways, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecr_images():
    aws_api.init_ecr_repositories()
    aws_api.init_ecr_images()
    aws_api.cache_objects(
        aws_api.ecr_images, configuration.aws_api_ecr_images_cache_file
    )
    assert isinstance(aws_api.ecr_images, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecr_repositories():
    aws_api.init_ecr_repositories()
    aws_api.cache_objects(
        aws_api.ecr_repositories, configuration.aws_api_ecr_repositories_cache_file
    )
    assert isinstance(aws_api.ecr_repositories, list)


# endregion


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecs_clusters():
    aws_api.init_ecs_clusters()
    aws_api.cache_objects(
        aws_api.ecs_clusters, configuration.aws_api_ecs_clusters_cache_file
    )
    assert isinstance(aws_api.ecs_clusters, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ec2_volumes():
    aws_api.init_ec2_volumes()
    aws_api.cache_objects(
        aws_api.ec2_volumes, configuration.aws_api_ec2_volumes_cache_file
    )
    assert isinstance(aws_api.ec2_volumes, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_stepfunctions_state_machines():
    ret = aws_api.stepfunctions_client.get_all_state_machines()
    aws_api.cache_objects(
        ret, configuration.aws_api_stepfunctions_state_machines_cache_file
    )
    assert isinstance(ret, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_eks_addons():
    ret = aws_api.init_eks_addons()
    assert isinstance(ret, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_eks_addons_from_cache():
    ret = aws_api.init_eks_addons(from_cache=True)
    assert isinstance(ret, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_eks_clusters():
    ret = aws_api.init_eks_clusters()
    assert isinstance(ret, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_eks_clusters_from_cache():
    ret = aws_api.init_eks_clusters(from_cache=True)
    assert isinstance(ret, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_auto_scaling_groups():
    aws_api.init_auto_scaling_groups()
    aws_api.cache_objects(
        aws_api.auto_scaling_groups,
        configuration.aws_api_auto_scaling_groups_cache_file,
    )
    assert isinstance(aws_api.auto_scaling_groups, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_auto_scaling_policies():
    aws_api.init_auto_scaling_policies()
    aws_api.cache_objects(
        aws_api.auto_scaling_policies,
        configuration.aws_api_auto_scaling_policies_cache_file,
    )
    assert isinstance(aws_api.auto_scaling_policies, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_application_auto_scaling_policies():
    aws_api.init_application_auto_scaling_policies()
    aws_api.cache_objects(
        aws_api.application_auto_scaling_policies,
        configuration.aws_api_application_auto_scaling_policies_cache_file,
    )
    assert isinstance(aws_api.application_auto_scaling_policies, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_application_auto_scaling_scalable_targets():
    aws_api.init_application_auto_scaling_scalable_targets()
    aws_api.cache_objects(
        aws_api.application_auto_scaling_scalable_targets,
        configuration.aws_api_application_auto_scaling_scalable_targets_cache_file,
    )
    assert isinstance(aws_api.application_auto_scaling_scalable_targets, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecs_capacity_providers():
    aws_api.init_ecs_capacity_providers()
    aws_api.cache_objects(
        aws_api.ecs_capacity_providers,
        configuration.aws_api_ecs_capacity_providers_cache_file,
    )
    assert isinstance(aws_api.ecs_capacity_providers, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecs_services():
    aws_api.init_ecs_clusters()
    aws_api.init_ecs_services()
    aws_api.cache_objects(
        aws_api.ecs_services, configuration.aws_api_ecs_services_cache_file
    )
    assert isinstance(aws_api.ecs_services, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecs_task_definitions():
    aws_api.init_ecs_task_definitions()
    aws_api.cache_objects(
        aws_api.ecs_task_definitions,
        configuration.aws_api_ecs_task_definitions_cache_file,
    )
    assert isinstance(aws_api.ecs_task_definitions, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_ecs_tasks():
    aws_api.init_ecs_tasks()
    aws_api.cache_objects(aws_api.ecs_tasks, configuration.aws_api_ecs_tasks_cache_file)
    assert isinstance(aws_api.ecs_tasks, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_sqs_queues():
    aws_api.init_sqs_queues()
    aws_api.cache_objects(
        aws_api.sqs_queues, configuration.aws_api_sqs_queues_cache_file
    )
    print(f"len(sqs_queues) = {len(aws_api.sqs_queues)}")
    assert isinstance(aws_api.sqs_queues, list)


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_lambda_event_source_mappings():
    aws_api.init_lambda_event_source_mappings()
    aws_api.cache_objects(
        aws_api.lambda_event_source_mappings,
        configuration.aws_api_lambda_event_source_mappings_cache_file,
    )
    print(
        f"len(lambda_event_source_mappings) = {len(aws_api.lambda_event_source_mappings)}"
    )
    assert isinstance(aws_api.lambda_event_source_mappings, list)


def find_stream():
    log_group_dir = "dirpath"
    for file_name in os.listdir(log_group_dir):
        print(f"checking {file_name}")
        with open(os.path.join(log_group_dir, file_name), encoding="utf-8") as fh:
            ret = json.load(fh)
        for dict_stream in ret:
            if "something" in dict_stream["logStreamName"]:
                print(dict_stream["logStreamName"])


def find_ami():
    region = "us-east-1"
    filter_request = {}
    filter_request["Filters"] = [
        {
            "Name": "owner-id",
            "Values": [
                "591542846629",
            ],
        }
    ]
    filter_request["Filters"] = [
        {
            "Name": "image-id",
            "Values": [
                "ami-0f06fc190dd71269e",
            ],
        }
    ]

    filter_request["Filters"] = [
        {
            "Name": "name",
            "Values": [
                "amzn2-ami-ecs-hvm-2.0.20201209-x86_64-ebs",
            ],
        }
    ]
    amis = aws_api.ec2_client.get_region_amis(region, custom_filters=filter_request)
    ami = amis[0]
    ami.print_dict_src()


@pytest.mark.skip(reason="No way of currently testing this")
def test_add_managed_region():
    region = Region.get_region("us-west-2")
    aws_api.add_managed_region(region)
    assert region in aws_api.get_managed_regions()


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_acm_certificates():
    aws_api.init_acm_certificates()
    aws_api.cache_objects(
        aws_api.acm_certificates, configuration.aws_api_acm_certificates_cache_file
    )
    print(f"len(acm_certificates) = {len(aws_api.acm_certificates)}")


@pytest.mark.skip(reason="No way of currently testing this")
def test_init_and_cache_kms_keys():
    aws_api.init_kms_keys()
    aws_api.cache_objects(aws_api.kms_keys, configuration.aws_api_kms_keys_cache_file)
    print(f"len(kms_keys) = {len(aws_api.kms_keys)}")
    assert isinstance(aws_api.kms_keys, list)


if __name__ == "__main__":
    #test_add_managed_region()

    #test_init_and_cache_amis()
    #test_init_and_cache_key_pairs()
    #test_init_and_cache_internet_gateways()
    #test_init_and_cache_vpc_peerings()
    #test_init_and_cache_route_tables()
    #test_init_and_cache_elastic_addresses()
    #test_init_and_cache_nat_gateways()
    #test_init_and_cache_ecr_repositories()
    #test_init_and_cache_ecs_clusters()
    #test_init_and_cache_ecs_services()
    #test_init_and_cache_ecs_capacity_providers()
    # todo: fix test_init_and_cache_ec2_launch_template_versions()
    # test_init_and_cache_ecs_task_definitions()
    # todo: fix test_init_and_cache_ecs_tasks()
    #test_init_and_cache_load_balancers()
    #test_init_and_cache_target_groups()
    # test_init_and_cache_acm_certificates()
    #test_init_and_cache_rds_db_instances()
    #test_init_and_cache_rds_db_clusters()
    #test_init_and_cache_rds_db_cluster_snapshots()
    #test_init_and_cache_kms_keys()
    #test_init_and_cache_rds_db_subnet_groups()
    #test_init_and_cache_rds_db_cluster_parameter_groups()
    #test_init_and_cache_rds_db_parameter_groups()
    #test_init_and_cache_s3_buckets()
    #test_init_and_cache_cloudfront_origin_access_identities()
    # test_init_and_cache_cloudfront_distributions()
    #test_init_and_cache_elasticache_clusters()
    #test_init_and_cache_elasticache_cache_parameter_groups()
    #test_init_and_cache_elasticache_cache_subnet_groups()
    #test_init_and_cache_elasticache_replication_groups()
    #todo: fix test_init_and_cache_elasticache_cache_security_groups()
    #test_init_and_cache_sqs_queues()
    #test_init_and_cache_lambda_event_source_mappings()
    #test_init_and_cache_event_bridge_rules()
    #test_init_and_cache_lambdas()
    #test_init_and_cache_lambda_event_source_mappings()
    #test_init_and_cache_servicediscovery_namespaces()
    # todo: fix test_init_and_cache_vpcs()
    test_init_and_cache_security_regions_groups()
    #test_init_and_cache_subnets()
    # todo: fix test_init_and_cache_glue_tables()
    # todo: fix test_init_and_cache_glue_databases()
    #test_init_and_cache_iam_instance_profiles()
    #test_init_and_cache_iam_groups()
    #test_init_and_cache_iam_users()
    #test_init_and_cache_iam_policies()
    #test_init_and_cache_dynamodb_tables()
    #test_init_and_cache_dynamodb_endpoints()
    #test_init_and_cache_sesv2_email_identities()
    #test_init_and_cache_sesv2_email_templates()
    #test_init_and_cache_sesv2_configuration_sets()
    #test_init_and_cache_sns_topics()
    #test_init_and_cache_sns_subscriptions()
    #test_init_and_cache_auto_scaling_groups()
    #test_init_and_cache_auto_scaling_policies()
    #test_init_and_cache_cloudwatch_alarms()
    #test_init_and_cache_application_auto_scaling_policies()
    #test_init_and_cache_application_auto_scaling_scalable_targets()
    #test_init_and_cache_spot_fleet_requests()
    # test_init_and_cache_ec2_instances()
    # test_init_and_cache_ec2_volumes()
    # test_init_and_cache_stepfunctions_state_machines()
    # test_init_eks_addons()
    # test_init_eks_addons_from_cache()
    # test_init_eks_clusters()
    # test_init_eks_clusters_from_cache()
    # test_init_and_cache_hosted_zones()
