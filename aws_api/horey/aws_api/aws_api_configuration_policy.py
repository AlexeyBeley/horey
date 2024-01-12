"""
AWS API config

"""

import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-lines, too-many-instance-attributes


class AWSAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._aws_api_regions = None
        self._accounts_file = None
        self._aws_api_account = None
        self._aws_api_accounts = None
        self._aws_api_cache_dir = None
        self._aws_api_cleanup_cache_dir = None
        self._aws_api_dynamodb_cache_dir = None

        self._aws_api_s3_cache_dir = None
        self._aws_api_pricing_cache_dir = None
        self._aws_api_s3_bucket_objects_cache_dir = None
        self._aws_api_ec2_cache_dir = None
        self._aws_api_lambda_cache_dir = None
        self._aws_api_cloudwatch_log_groups_cache_dir = None
        self._aws_api_cloudwatch_log_groups_streams_cache_dir = None
        self._aws_api_cloudwatch_metrics_cache_dir = None
        self._aws_api_classic_loadbalancers_cache_dir = None
        self._aws_api_loadbalancers_cache_dir = None
        self._aws_api_rds_cache_dir = None
        self._aws_api_hosted_zones_cache_dir = None
        self._aws_api_cloudfront_cache_dir = None
        self._aws_api_iam_cache_dir = None
        self._aws_api_iam_policies_cache_dir = None
        self._aws_api_iam_roles_cache_dir = None
        self._aws_api_event_bridge_cache_dir = None
        self._aws_api_servicediscovery_cache_dir = None
        self._aws_api_elasticsearch_cache_dir = None
        self._aws_api_ecr_cache_dir = None
        self._aws_api_ecs_cache_dir = None
        self._aws_api_auto_scaling_cache_dir = None
        self._aws_api_application_auto_scaling_cache_dir = None
        self._aws_api_acm_cache_dir = None
        self._aws_api_kms_cache_dir = None
        self._aws_api_elasticache_cache_dir = None
        self._aws_api_sqs_cache_dir = None
        self._aws_api_glue_cache_dir = None
        self._aws_api_stepfunctions_cache_dir = None
        self._aws_api_sesv2_cache_dir = None
        self._aws_api_sns_cache_dir = None

    @property
    def aws_api_regions(self):
        if self._aws_api_regions is None:
            raise ValueError("aws_api_regions were not set")
        return self._aws_api_regions

    @aws_api_regions.setter
    def aws_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(
                f"aws_api_regions must be a list received {value} of type: {type(value)}"
            )

        self._aws_api_regions = value

    @property
    def aws_api_account(self):
        if self._aws_api_account is None:
            raise ValueError("aws_api_account was not set")
        return self._aws_api_account

    @aws_api_account.setter
    def aws_api_account(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"aws_api_account must be a string received {value} of type: {type(value)}"
            )
        self._aws_api_account = value

    @property
    def aws_api_accounts(self):
        if self._aws_api_accounts is None:
            raise ValueError("aws_api_account was not set")
        return self._aws_api_accounts

    @aws_api_accounts.setter
    def aws_api_accounts(self, value):
        if not isinstance(value, list):
            raise ValueError(
                f"aws_api_account must be a list received {value} of type: {type(value)}"
            )
        self._aws_api_accounts = value

    @property
    def aws_api_cache_dir(self):
        if self._aws_api_cache_dir is None:
            raise ValueError("aws_api_cache_dir was not set")
        return self._aws_api_cache_dir

    @aws_api_cache_dir.setter
    def aws_api_cache_dir(self, value):
        self._aws_api_cache_dir = value
        os.makedirs(self._aws_api_cache_dir, exist_ok=True)

    # region s3

    @property
    def aws_api_s3_cache_dir(self):
        if self._aws_api_s3_cache_dir is None:
            self._aws_api_s3_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "s3"
            )
            os.makedirs(self._aws_api_s3_cache_dir, exist_ok=True)
        return self._aws_api_s3_cache_dir

    @aws_api_s3_cache_dir.setter
    def aws_api_s3_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_s3_buckets_cache_file(self):
        return os.path.join(self.aws_api_s3_cache_dir, "buckets.json")

    @aws_api_s3_buckets_cache_file.setter
    def aws_api_s3_buckets_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_s3_bucket_objects_cache_dir(self):
        if self._aws_api_s3_bucket_objects_cache_dir is None:
            self._aws_api_s3_bucket_objects_cache_dir = os.path.join(
                self.aws_api_s3_cache_dir, "s3_buckets_objects"
            )
            os.makedirs(self._aws_api_s3_bucket_objects_cache_dir, exist_ok=True)
        return self._aws_api_s3_bucket_objects_cache_dir

    @aws_api_s3_bucket_objects_cache_dir.setter
    def aws_api_s3_bucket_objects_cache_dir(self, value):
        raise ValueError(value)

    # endregion

    # region cloudwatch
    @property
    def aws_api_cloudwatch_cache_dir(self):
        if self._aws_api_cloudwatch_log_groups_cache_dir is None:
            self._aws_api_cloudwatch_log_groups_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "cloudwatch"
            )
            os.makedirs(self._aws_api_cloudwatch_log_groups_cache_dir, exist_ok=True)
        return self._aws_api_cloudwatch_log_groups_cache_dir

    @aws_api_cloudwatch_cache_dir.setter
    def aws_api_cloudwatch_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudwatch_log_groups_streams_cache_dir(self):
        if self._aws_api_cloudwatch_log_groups_streams_cache_dir is None:
            self._aws_api_cloudwatch_log_groups_streams_cache_dir = os.path.join(
                self.aws_api_cloudwatch_cache_dir, "streams"
            )
            os.makedirs(
                self._aws_api_cloudwatch_log_groups_streams_cache_dir, exist_ok=True
            )
        return self._aws_api_cloudwatch_log_groups_streams_cache_dir

    @aws_api_cloudwatch_log_groups_streams_cache_dir.setter
    def aws_api_cloudwatch_log_groups_streams_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudwatch_metrics_cache_dir(self):
        if self._aws_api_cloudwatch_metrics_cache_dir is None:
            self._aws_api_cloudwatch_metrics_cache_dir = os.path.join(
                self.aws_api_cloudwatch_cache_dir, "metrics"
            )
            os.makedirs(self._aws_api_cloudwatch_metrics_cache_dir, exist_ok=True)
        return self._aws_api_cloudwatch_metrics_cache_dir

    @aws_api_cloudwatch_metrics_cache_dir.setter
    def aws_api_cloudwatch_metrics_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudwatch_log_groups_cache_file(self):
        return os.path.join(
            self.aws_api_cloudwatch_cache_dir, "cloudwatch_log_groups.json"
        )

    @aws_api_cloudwatch_log_groups_cache_file.setter
    def aws_api_cloudwatch_log_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudwatch_alarms_cache_file(self):
        return os.path.join(self.aws_api_cloudwatch_cache_dir, "cloudwatch_alarms.json")

    @aws_api_cloudwatch_alarms_cache_file.setter
    def aws_api_cloudwatch_alarms_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudwatch_log_groups_metric_filters_cache_file(self):
        return os.path.join(
            self.aws_api_cloudwatch_cache_dir,
            "cloudwatch_log_groups_metric_filters.json",
        )

    @aws_api_cloudwatch_log_groups_metric_filters_cache_file.setter
    def aws_api_cloudwatch_log_groups_metric_filters_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region ec2
    @property
    def aws_api_ec2_cache_dir(self):
        if self._aws_api_ec2_cache_dir is None:
            self._aws_api_ec2_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "ec2"
            )
            os.makedirs(self._aws_api_ec2_cache_dir, exist_ok=True)
        return self._aws_api_ec2_cache_dir

    @aws_api_ec2_cache_dir.setter
    def aws_api_ec2_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_ec2_instances_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "instances.json")

    @aws_api_ec2_instances_cache_file.setter
    def aws_api_ec2_instances_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ec2_volumes_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "volumes.json")

    @aws_api_ec2_volumes_cache_file.setter
    def aws_api_ec2_volumes_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_spot_fleet_requests_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "spot_fleet_requests.json")

    @property
    def aws_api_ec2_security_groups_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "network_security_groups.json")

    @aws_api_ec2_security_groups_cache_file.setter
    def aws_api_ec2_security_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ec2_launch_templates_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "ec2_launch_templates.json")

    @aws_api_ec2_launch_templates_cache_file.setter
    def aws_api_ec2_launch_templates_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ec2_launch_template_versions_cache_file(self):
        return os.path.join(
            self.aws_api_ec2_cache_dir, "ec2_launch_template_versions.json"
        )

    @aws_api_ec2_launch_template_versions_cache_file.setter
    def aws_api_ec2_launch_template_versions_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ec2_network_interfaces_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "network_interfaces.json")

    @aws_api_ec2_network_interfaces_cache_file.setter
    def aws_api_ec2_network_interfaces_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_managed_prefix_lists_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "managed_prefix_lists.json")

    @aws_api_managed_prefix_lists_cache_file.setter
    def aws_api_managed_prefix_lists_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_vpcs_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "vpcs.json")

    @aws_api_vpcs_cache_file.setter
    def aws_api_vpcs_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_subnets_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "subnets.json")

    @aws_api_subnets_cache_file.setter
    def aws_api_subnets_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_availability_zones_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "availability_zones.json")

    @aws_api_availability_zones_cache_file.setter
    def aws_api_availability_zones_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_amis_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "amis.json")

    @aws_api_amis_cache_file.setter
    def aws_api_amis_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_key_pairs_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "key_pairs.json")

    @aws_api_key_pairs_cache_file.setter
    def aws_api_key_pairs_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_internet_gateways_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "internet_gateways.json")

    @aws_api_internet_gateways_cache_file.setter
    def aws_api_internet_gateways_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_vpc_peerings_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "vpc_peerings.json")

    @aws_api_vpc_peerings_cache_file.setter
    def aws_api_vpc_peerings_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_route_tables_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "route_tables.json")

    @aws_api_route_tables_cache_file.setter
    def aws_api_route_tables_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_elastic_addresses_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "elastic_addresses.json")

    @aws_api_elastic_addresses_cache_file.setter
    def aws_api_elastic_addresses_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_nat_gateways_cache_file(self):
        return os.path.join(self.aws_api_ec2_cache_dir, "nat_gateways.json")

    @aws_api_nat_gateways_cache_file.setter
    def aws_api_nat_gateways_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region glue
    @property
    def aws_api_glue_cache_dir(self):
        if self._aws_api_glue_cache_dir is None:
            self._aws_api_glue_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "glue"
            )
            os.makedirs(self._aws_api_glue_cache_dir, exist_ok=True)
        return self._aws_api_glue_cache_dir

    @property
    def aws_api_glue_databases_cache_file(self):
        return os.path.join(self.aws_api_glue_cache_dir, "glue_databases.json")

    @aws_api_glue_databases_cache_file.setter
    def aws_api_glue_databases_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_glue_tables_cache_file(self):
        return os.path.join(self.aws_api_glue_cache_dir, "glue_tables.json")

    @aws_api_glue_tables_cache_file.setter
    def aws_api_glue_tables_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region stepfunctions
    @property
    def aws_api_stepfunctions_cache_dir(self):
        if self._aws_api_stepfunctions_cache_dir is None:
            self._aws_api_stepfunctions_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "stepfunctions"
            )
            os.makedirs(self._aws_api_stepfunctions_cache_dir, exist_ok=True)
        return self._aws_api_stepfunctions_cache_dir

    @property
    def aws_api_stepfunctions_state_machines_cache_file(self):
        return os.path.join(self.aws_api_stepfunctions_cache_dir, "stepfunctions_state_machines.json")

    # endregion

    # region lambda
    @property
    def aws_api_lambda_cache_dir(self):
        if self._aws_api_lambda_cache_dir is None:
            self._aws_api_lambda_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "lambda"
            )
            os.makedirs(self._aws_api_lambda_cache_dir, exist_ok=True)
        return self._aws_api_lambda_cache_dir

    @aws_api_lambda_cache_dir.setter
    def aws_api_lambda_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_lambdas_cache_file(self):
        return os.path.join(self.aws_api_lambda_cache_dir, "lambdas.json")

    @aws_api_lambdas_cache_file.setter
    def aws_api_lambdas_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_lambda_event_source_mappings_cache_file(self):
        return os.path.join(
            self.aws_api_lambda_cache_dir, "lambda_event_source_mappings.json"
        )

    @aws_api_lambda_event_source_mappings_cache_file.setter
    def aws_api_lambda_event_source_mappings_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region ecr
    @property
    def aws_api_ecr_cache_dir(self):
        if self._aws_api_ecr_cache_dir is None:
            self._aws_api_ecr_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "ecr"
            )
            os.makedirs(self._aws_api_ecr_cache_dir, exist_ok=True)
        return self._aws_api_ecr_cache_dir

    @aws_api_ecr_cache_dir.setter
    def aws_api_ecr_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_ecr_images_cache_file(self):
        return os.path.join(self.aws_api_ecr_cache_dir, "ecr_images.json")

    @aws_api_ecr_images_cache_file.setter
    def aws_api_ecr_images_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ecr_repositories_cache_file(self):
        return os.path.join(self.aws_api_ecr_cache_dir, "ecr_repositories.json")

    @aws_api_ecr_repositories_cache_file.setter
    def aws_api_ecr_repositories_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region classic_loadbalancers
    @property
    def aws_api_classic_loadbalancers_cache_dir(self):
        if self._aws_api_classic_loadbalancers_cache_dir is None:
            self._aws_api_classic_loadbalancers_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "classic_loadbalancers"
            )
            os.makedirs(self._aws_api_classic_loadbalancers_cache_dir, exist_ok=True)
        return self._aws_api_classic_loadbalancers_cache_dir

    @aws_api_classic_loadbalancers_cache_dir.setter
    def aws_api_classic_loadbalancers_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_classic_loadbalancers_cache_file(self):
        return os.path.join(
            self.aws_api_classic_loadbalancers_cache_dir, "classic_loadbalancers.json"
        )

    @aws_api_classic_loadbalancers_cache_file.setter
    def aws_api_classic_loadbalancers_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region loadbalancers
    @property
    def aws_api_loadbalancers_cache_dir(self):
        if self._aws_api_loadbalancers_cache_dir is None:
            self._aws_api_loadbalancers_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "loadbalancers"
            )
            os.makedirs(self._aws_api_loadbalancers_cache_dir, exist_ok=True)
        return self._aws_api_loadbalancers_cache_dir

    @aws_api_loadbalancers_cache_dir.setter
    def aws_api_loadbalancers_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_loadbalancers_cache_file(self):
        return os.path.join(self.aws_api_loadbalancers_cache_dir, "loadbalancers.json")

    @aws_api_loadbalancers_cache_file.setter
    def aws_api_loadbalancers_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_loadbalancer_target_groups_cache_file(self):
        return os.path.join(
            self.aws_api_loadbalancers_cache_dir, "loadbalancer_target_groups.json"
        )

    @aws_api_loadbalancer_target_groups_cache_file.setter
    def aws_api_loadbalancer_target_groups_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region iam
    @property
    def aws_api_iam_cache_dir(self):
        if self._aws_api_iam_cache_dir is None:
            self._aws_api_iam_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "iam"
            )
            os.makedirs(self.aws_api_iam_cache_dir, exist_ok=True)
        return self._aws_api_iam_cache_dir

    @aws_api_iam_cache_dir.setter
    def aws_api_iam_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_iam_policies_cache_dir(self):
        if self._aws_api_iam_policies_cache_dir is None:
            self._aws_api_iam_policies_cache_dir = os.path.join(
                self.aws_api_iam_cache_dir, "policies"
            )
            os.makedirs(self._aws_api_iam_policies_cache_dir, exist_ok=True)
        return self._aws_api_iam_policies_cache_dir

    @aws_api_iam_policies_cache_dir.setter
    def aws_api_iam_policies_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_iam_roles_cache_dir(self):
        if self._aws_api_iam_roles_cache_dir is None:
            self._aws_api_iam_roles_cache_dir = os.path.join(
                self.aws_api_iam_cache_dir, "roles"
            )
            os.makedirs(self._aws_api_iam_roles_cache_dir, exist_ok=True)
        return self._aws_api_iam_roles_cache_dir

    @aws_api_iam_roles_cache_dir.setter
    def aws_api_iam_roles_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_iam_policies_cache_file(self):
        return os.path.join(self.aws_api_iam_policies_cache_dir, "policies.json")

    @aws_api_iam_policies_cache_file.setter
    def aws_api_iam_policies_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_iam_roles_cache_file(self):
        return os.path.join(self.aws_api_iam_roles_cache_dir, "roles.json")

    @aws_api_iam_roles_cache_file.setter
    def aws_api_iam_roles_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_iam_instance_profiles_cache_file(self):
        return os.path.join(self.aws_api_iam_roles_cache_dir, "instance_profiles.json")

    @property
    def aws_api_iam_groups_cache_file(self):
        return os.path.join(self.aws_api_iam_roles_cache_dir, "groups.json")

    @aws_api_iam_instance_profiles_cache_file.setter
    def aws_api_iam_instance_profiles_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_iam_users_cache_file(self):
        return os.path.join(self.aws_api_iam_cache_dir, "users.json")

    # endregion

    # region databases
    @property
    def aws_api_rds_cache_dir(self):
        if self._aws_api_rds_cache_dir is None:
            self._aws_api_rds_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "rds"
            )
            os.makedirs(self._aws_api_rds_cache_dir, exist_ok=True)
        return self._aws_api_rds_cache_dir

    @aws_api_rds_cache_dir.setter
    def aws_api_rds_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_rds_db_instances_cache_file(self):
        return os.path.join(self.aws_api_rds_cache_dir, "rds_db_instances.json")

    @aws_api_rds_db_instances_cache_file.setter
    def aws_api_rds_db_instances_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_rds_db_clusters_cache_file(self):
        return os.path.join(self.aws_api_rds_cache_dir, "rds_db_clusters.json")

    @aws_api_rds_db_clusters_cache_file.setter
    def aws_api_rds_db_clusters_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_rds_db_subnet_groups_cache_file(self):
        return os.path.join(self.aws_api_rds_cache_dir, "rds_db_subnet_groups.json")

    @aws_api_rds_db_subnet_groups_cache_file.setter
    def aws_api_rds_db_subnet_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_rds_db_parameter_groups_cache_file(self):
        return os.path.join(self.aws_api_rds_cache_dir, "rds_db_parameter_groups.json")

    @aws_api_rds_db_parameter_groups_cache_file.setter
    def aws_api_rds_db_parameter_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_rds_db_cluster_parameter_groups_cache_file(self):
        return os.path.join(
            self.aws_api_rds_cache_dir, "rds_db_cluster_parameter_groups.json"
        )

    @aws_api_rds_db_cluster_parameter_groups_cache_file.setter
    def aws_api_rds_db_cluster_parameter_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_rds_db_cluster_snapshots_cache_file(self):
        return os.path.join(self.aws_api_rds_cache_dir, "rds_db_cluster_snapshots.json")

    @aws_api_rds_db_cluster_snapshots_cache_file.setter
    def aws_api_rds_db_cluster_snapshots_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region elasticache
    @property
    def aws_api_elasticache_cache_dir(self):
        if self._aws_api_elasticache_cache_dir is None:
            self._aws_api_elasticache_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "elasticache"
            )
            os.makedirs(self._aws_api_elasticache_cache_dir, exist_ok=True)
        return self._aws_api_elasticache_cache_dir

    @aws_api_elasticache_cache_dir.setter
    def aws_api_elasticache_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_elasticache_clusters_cache_file(self):
        return os.path.join(
            self.aws_api_elasticache_cache_dir, "elasticache_clusters.json"
        )

    @aws_api_elasticache_clusters_cache_file.setter
    def aws_api_elasticache_clusters_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_elasticache_cache_subnet_groups_cache_file(self):
        return os.path.join(
            self.aws_api_elasticache_cache_dir, "elasticache_cache_subnet_groups.json"
        )

    @aws_api_elasticache_cache_subnet_groups_cache_file.setter
    def aws_api_elasticache_cache_subnet_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_elasticache_cache_security_groups_cache_file(self):
        return os.path.join(
            self.aws_api_elasticache_cache_dir, "elasticache_cache_security_groups.json"
        )

    @aws_api_elasticache_cache_security_groups_cache_file.setter
    def aws_api_elasticache_cache_security_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_elasticache_cache_parameter_groups_cache_file(self):
        return os.path.join(
            self.aws_api_elasticache_cache_dir,
            "elasticache_cache_parameter_groups.json",
        )

    @aws_api_elasticache_cache_parameter_groups_cache_file.setter
    def aws_api_elasticache_cache_parameter_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_elasticache_replication_groups_cache_file(self):
        return os.path.join(
            self.aws_api_elasticache_cache_dir, "elasticache_replication_groups.json"
        )

    @aws_api_elasticache_replication_groups_cache_file.setter
    def aws_api_elasticache_replication_groups_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region hosted_zones
    @property
    def aws_api_hosted_zones_cache_dir(self):
        if self._aws_api_hosted_zones_cache_dir is None:
            self._aws_api_hosted_zones_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "hosted_zones"
            )
            os.makedirs(self._aws_api_hosted_zones_cache_dir, exist_ok=True)
        return self._aws_api_hosted_zones_cache_dir

    @aws_api_hosted_zones_cache_dir.setter
    def aws_api_hosted_zones_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_hosted_zones_cache_file(self):
        return os.path.join(self.aws_api_hosted_zones_cache_dir, "hosted_zones.json")

    @aws_api_hosted_zones_cache_file.setter
    def aws_api_hosted_zones_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region cloudfront
    @property
    def aws_api_cloudfront_cache_dir(self):
        if self._aws_api_cloudfront_cache_dir is None:
            self._aws_api_cloudfront_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "cloudfront"
            )
            os.makedirs(self._aws_api_cloudfront_cache_dir, exist_ok=True)
        return self._aws_api_cloudfront_cache_dir

    @aws_api_cloudfront_cache_dir.setter
    def aws_api_cloudfront_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudfront_distributions_cache_file(self):
        return os.path.join(
            self.aws_api_cloudfront_cache_dir, "cloudfront_distributions.json"
        )

    @aws_api_cloudfront_distributions_cache_file.setter
    def aws_api_cloudfront_distributions_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cloudfront_origin_access_identities_cache_file(self):
        return os.path.join(
            self.aws_api_cloudfront_cache_dir,
            "cloudfront_origin_access_identities.json",
        )

    @aws_api_cloudfront_origin_access_identities_cache_file.setter
    def aws_api_cloudfront_origin_access_identities_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region event_bridge
    @property
    def aws_api_event_bridge_cache_dir(self):
        if self._aws_api_event_bridge_cache_dir is None:
            self._aws_api_event_bridge_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "event_bridge"
            )
            os.makedirs(self._aws_api_event_bridge_cache_dir, exist_ok=True)
        return self._aws_api_event_bridge_cache_dir

    @aws_api_event_bridge_cache_dir.setter
    def aws_api_event_bridge_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_event_bridge_rules_cache_file(self):
        return os.path.join(
            self.aws_api_event_bridge_cache_dir, "event_bridge_rules.json"
        )

    @aws_api_event_bridge_rules_cache_file.setter
    def aws_api_event_bridge_rules_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region servicediscovery
    @property
    def aws_api_servicediscovery_cache_dir(self):
        if self._aws_api_servicediscovery_cache_dir is None:
            self._aws_api_servicediscovery_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "servicediscovery"
            )
            os.makedirs(self._aws_api_servicediscovery_cache_dir, exist_ok=True)
        return self._aws_api_servicediscovery_cache_dir

    @aws_api_servicediscovery_cache_dir.setter
    def aws_api_servicediscovery_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_servicediscovery_services_cache_file(self):
        return os.path.join(
            self.aws_api_servicediscovery_cache_dir, "servicediscovery_services.json"
        )

    @aws_api_servicediscovery_services_cache_file.setter
    def aws_api_servicediscovery_services_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_servicediscovery_namespaces_cache_file(self):
        return os.path.join(
            self.aws_api_servicediscovery_cache_dir, "servicediscovery_namespaces.json"
        )

    @aws_api_servicediscovery_namespaces_cache_file.setter
    def aws_api_servicediscovery_namespaces_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region elasticsearch
    @property
    def aws_api_elasticsearch_cache_dir(self):
        if self._aws_api_elasticsearch_cache_dir is None:
            self._aws_api_elasticsearch_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "elasticsearch"
            )
            os.makedirs(self._aws_api_elasticsearch_cache_dir, exist_ok=True)
        return self._aws_api_elasticsearch_cache_dir

    @aws_api_elasticsearch_cache_dir.setter
    def aws_api_elasticsearch_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_elasticsearch_domains_cache_file(self):
        return os.path.join(
            self.aws_api_elasticsearch_cache_dir, "elasticsearch_domains.json"
        )

    @aws_api_elasticsearch_domains_cache_file.setter
    def aws_api_elasticsearch_domains_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region ecs
    @property
    def aws_api_ecs_cache_dir(self):
        if self._aws_api_ecs_cache_dir is None:
            self._aws_api_ecs_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "ecs"
            )
            os.makedirs(self._aws_api_ecs_cache_dir, exist_ok=True)
        return self._aws_api_ecs_cache_dir

    @aws_api_ecs_cache_dir.setter
    def aws_api_ecs_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_ecs_clusters_cache_file(self):
        return os.path.join(self.aws_api_ecs_cache_dir, "ecs_clusters.json")

    @aws_api_ecs_clusters_cache_file.setter
    def aws_api_ecs_clusters_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ecs_capacity_providers_cache_file(self):
        return os.path.join(self.aws_api_ecs_cache_dir, "ecs_capacity_providers.json")

    @aws_api_ecs_capacity_providers_cache_file.setter
    def aws_api_ecs_capacity_providers_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ecs_services_cache_file(self):
        return os.path.join(self.aws_api_ecs_cache_dir, "ecs_services.json")

    @aws_api_ecs_services_cache_file.setter
    def aws_api_ecs_services_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_ecs_task_definitions_cache_file(self):
        return os.path.join(self.aws_api_ecs_cache_dir, "ecs_task_definitions.json")

    @property
    def aws_api_ecs_tasks_cache_file(self):
        return os.path.join(self.aws_api_ecs_cache_dir, "ecs_tasks.json")

    # endregion

    # region sqs
    @property
    def aws_api_sqs_cache_dir(self):
        if self._aws_api_sqs_cache_dir is None:
            self._aws_api_sqs_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "sqs"
            )
            os.makedirs(self._aws_api_sqs_cache_dir, exist_ok=True)
        return self._aws_api_sqs_cache_dir

    @aws_api_sqs_cache_dir.setter
    def aws_api_sqs_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_sqs_queues_cache_file(self):
        return os.path.join(self.aws_api_sqs_cache_dir, "sqs_queues.json")

    @aws_api_sqs_queues_cache_file.setter
    def aws_api_sqs_queues_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region auto_scaling
    @property
    def aws_api_auto_scaling_cache_dir(self):
        if self._aws_api_auto_scaling_cache_dir is None:
            self._aws_api_auto_scaling_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "auto_scaling"
            )
            os.makedirs(self._aws_api_auto_scaling_cache_dir, exist_ok=True)
        return self._aws_api_auto_scaling_cache_dir

    @aws_api_auto_scaling_cache_dir.setter
    def aws_api_auto_scaling_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_auto_scaling_groups_cache_file(self):
        return os.path.join(
            self.aws_api_auto_scaling_cache_dir, "auto_scaling_groups.json"
        )

    @aws_api_auto_scaling_groups_cache_file.setter
    def aws_api_auto_scaling_groups_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_auto_scaling_policies_cache_file(self):
        return os.path.join(
            self.aws_api_auto_scaling_cache_dir, "auto_scaling_policies.json"
        )

    # endregion

    # region application_auto_scaling
    @property
    def aws_api_application_auto_scaling_cache_dir(self):
        if self._aws_api_application_auto_scaling_cache_dir is None:
            self._aws_api_application_auto_scaling_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "application_auto_scaling"
            )
            os.makedirs(self._aws_api_application_auto_scaling_cache_dir, exist_ok=True)
        return self._aws_api_application_auto_scaling_cache_dir

    @aws_api_application_auto_scaling_cache_dir.setter
    def aws_api_application_auto_scaling_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_application_auto_scaling_scalable_targets_cache_file(self):
        return os.path.join(
            self.aws_api_application_auto_scaling_cache_dir,
            "application_auto_scaling_scalable_targets.json",
        )

    @property
    def aws_api_application_auto_scaling_policies_cache_file(self):
        return os.path.join(
            self.aws_api_application_auto_scaling_cache_dir,
            "application_auto_scaling_policies.json",
        )

    # endregion

    # region acm
    @property
    def aws_api_acm_cache_dir(self):
        if self._aws_api_acm_cache_dir is None:
            self._aws_api_acm_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "acm"
            )
            os.makedirs(self._aws_api_acm_cache_dir, exist_ok=True)
        return self._aws_api_acm_cache_dir

    @aws_api_acm_cache_dir.setter
    def aws_api_acm_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_acm_certificates_cache_file(self):
        return os.path.join(self.aws_api_acm_cache_dir, "acm_certificates.json")

    @aws_api_acm_certificates_cache_file.setter
    def aws_api_acm_certificates_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region kms
    @property
    def aws_api_kms_cache_dir(self):
        if self._aws_api_kms_cache_dir is None:
            self._aws_api_kms_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "kms"
            )
            os.makedirs(self._aws_api_kms_cache_dir, exist_ok=True)
        return self._aws_api_kms_cache_dir

    @aws_api_kms_cache_dir.setter
    def aws_api_kms_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_kms_keys_cache_file(self):
        return os.path.join(self.aws_api_kms_cache_dir, "kms_keys.json")

    @aws_api_kms_keys_cache_file.setter
    def aws_api_kms_keys_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region cleanup
    @property
    def aws_api_cleanup_reports_dir(self):
        if self._aws_api_cleanup_cache_dir is None:
            self._aws_api_cleanup_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "cleanup"
            )
            os.makedirs(self._aws_api_cleanup_cache_dir, exist_ok=True)
        return self._aws_api_cleanup_cache_dir

    @aws_api_cleanup_reports_dir.setter
    def aws_api_cleanup_reports_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanups_network_interfaces_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "network_interfaces.txt")

    @property
    def aws_api_cleanups_ecs_report_file_template(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "{region_mark}_ecs_resources_utilization.txt")

    @property
    def aws_api_cleanups_security_groups_report_file(self):
        return os.path.join(
            self.aws_api_cleanup_reports_dir, "network_security_groups.txt"
        )

    @property
    def aws_api_cleanups_iam_roles_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "iam_roles.txt")

    @property
    def aws_api_cleanups_ec2_instnaces_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "ec2_instances.txt")

    @property
    def aws_api_cleanups_ebs_volumes_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "ebs_volumes.txt")

    @property
    def aws_api_cleanups_iam_policies_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "iam_policies.txt")

    @property
    def aws_api_cleanups_lambda_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "lambda.txt")

    @aws_api_cleanups_lambda_file.setter
    def aws_api_cleanups_lambda_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanups_loadbalancers_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "loadbalancers.txt")

    @aws_api_cleanups_loadbalancers_report_file.setter
    def aws_api_cleanups_loadbalancers_report_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanups_s3_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "s3_report.txt")

    @aws_api_cleanups_s3_report_file.setter
    def aws_api_cleanups_s3_report_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanups_s3_summarized_data_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "s3_cleanup_data.json")

    @aws_api_cleanups_s3_summarized_data_file.setter
    def aws_api_cleanups_s3_summarized_data_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanup_cloudwatch_logs_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "cloudwatch_report.txt")

    @aws_api_cleanup_cloudwatch_logs_report_file.setter
    def aws_api_cleanup_cloudwatch_logs_report_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanup_cloudwatch_metrics_report_file(self):
        return os.path.join(
            self.aws_api_cleanup_reports_dir, "cloudwatch_metrics_report.txt"
        )

    @aws_api_cleanup_cloudwatch_metrics_report_file.setter
    def aws_api_cleanup_cloudwatch_metrics_report_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_cleanups_dns_report_file(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "dns_report.txt")

    @property
    def aws_api_cleanups_ec2_pricing_file_template(self):
        return os.path.join(self.aws_api_cleanup_reports_dir, "{region_mark}_ec2_pricing.txt")

    @aws_api_cleanups_dns_report_file.setter
    def aws_api_cleanups_dns_report_file(self, value):
        raise ValueError(value)

    @property
    def accounts_file(self):
        return self._accounts_file

    @accounts_file.setter
    def accounts_file(self, value):
        self._accounts_file = value

    # endregion

    # region dynamodb
    @property
    def aws_api_dynamodb_cache_dir(self):
        if self._aws_api_dynamodb_cache_dir is None:
            self._aws_api_dynamodb_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "dynamodb"
            )
            os.makedirs(self._aws_api_dynamodb_cache_dir, exist_ok=True)
        return self._aws_api_dynamodb_cache_dir

    @aws_api_dynamodb_cache_dir.setter
    def aws_api_dynamodb_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_dynamodb_tables_cache_file(self):
        return os.path.join(self.aws_api_dynamodb_cache_dir, "dynamodb_tables.json")

    @aws_api_dynamodb_tables_cache_file.setter
    def aws_api_dynamodb_tables_cache_file(self, value):
        raise ValueError(value)

    @property
    def aws_api_dynamodb_endpoints_cache_file(self):
        return os.path.join(self.aws_api_dynamodb_cache_dir, "dynamodb_endpoints.json")

    @aws_api_dynamodb_endpoints_cache_file.setter
    def aws_api_dynamodb_endpoints_cache_file(self, value):
        raise ValueError(value)

    # endregion

    # region sesv2
    @property
    def aws_api_sesv2_cache_dir(self):
        if self._aws_api_sesv2_cache_dir is None:
            self._aws_api_sesv2_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "sesv2"
            )
            os.makedirs(self._aws_api_sesv2_cache_dir, exist_ok=True)
        return self._aws_api_sesv2_cache_dir

    @aws_api_sesv2_cache_dir.setter
    def aws_api_sesv2_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_sesv2_email_identities_cache_file(self):
        return os.path.join(self.aws_api_sesv2_cache_dir, "sesv2_email_identities.json")

    @property
    def aws_api_sesv2_configuration_sets_cache_file(self):
        return os.path.join(
            self.aws_api_sesv2_cache_dir, "sesv2_configuration_sets.json"
        )

    @property
    def aws_api_sesv2_email_templates_cache_file(self):
        return os.path.join(self.aws_api_sesv2_cache_dir, "sesv2_email_templates.json")

    # endregion

    # region sns
    @property
    def aws_api_sns_cache_dir(self):
        if self._aws_api_sns_cache_dir is None:
            self._aws_api_sns_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "sns"
            )
            os.makedirs(self._aws_api_sns_cache_dir, exist_ok=True)
        return self._aws_api_sns_cache_dir

    @aws_api_sns_cache_dir.setter
    def aws_api_sns_cache_dir(self, value):
        raise ValueError(value)

    @property
    def aws_api_sns_subscriptions_cache_file(self):
        return os.path.join(self.aws_api_sns_cache_dir, "sns_subscriptions.json")

    @property
    def aws_api_sns_topics_cache_file(self):
        return os.path.join(self.aws_api_sns_cache_dir, "sns_topics.json")

    # endregion

    # region pricing
    @property
    def pricing_cache_dir(self):
        if self._aws_api_pricing_cache_dir is None:
            self._aws_api_pricing_cache_dir = os.path.join(
                self.aws_api_cache_dir, self.aws_api_account, "pricing"
            )
            os.makedirs(self._aws_api_pricing_cache_dir, exist_ok=True)
        return self._aws_api_pricing_cache_dir

    @property
    def pricing_file_path_template(self):
        region_dir = os.path.join(self.pricing_cache_dir, "{region_mark}")
        return os.path.join(region_dir, "{service_code}.json")

    # endregion
