"""
Init and cache AWS objects.

"""

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy

# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api = AWSAPI()


# pylint: disable= missing-function-docstring


@pytest.fixture(name="configuration")
def fixture_configuration():
    _configuration = EnvironmentAPIConfigurationPolicy()
    _configuration.project_name = "henvironment"
    _configuration.region = "us-west-2"
    _configuration.vpc_primary_subnet = "192.168.0.0/16"
    _configuration.tags = [{
        "Key": "Owner",
        "Value": "Horey"
    }]
    _configuration.vpc_name = "henvironment"
    _configuration.availability_zones_count = 3
    _configuration.subnet_mask_length = 24
    _configuration.subnet_name_template = "subnet-{type}-{id}"
    _configuration.route_table_name_template = "rt-{subnet}"
    _configuration.internet_gateway_name = f"igw-{_configuration.vpc_name}"
    _configuration.container_instance_security_group_name = f"sg_container_instance_{_configuration.vpc_name}"
    _configuration.secrets_manager_region = _configuration.region
    _configuration.container_instance_ssh_key_pair_name = f"container_instance_{_configuration.vpc_name}"
    _configuration.container_instance_launch_template_name = f"lt_container_instance_{_configuration.vpc_name}"
    _configuration.ecs_cluster_name = f"cluster_{_configuration.vpc_name}"
    _configuration.container_instance_role_name = f"role_container_instance_{_configuration.vpc_name}"
    _configuration.iam_path = f"/{_configuration.vpc_name}/"
    _configuration.container_instance_profile_name = f"instance_profile_container_instance_{_configuration.vpc_name}"
    _configuration.container_instance_auto_scaling_group_name = f"asg_container_instance_{_configuration.project_name}"
    _configuration.container_instance_auto_scaling_group_min_size = 1
    _configuration.container_instance_auto_scaling_group_max_size = 5
    _configuration.container_instance_capacity_provider_name = f"cp_ci_{_configuration.project_name}"
    _configuration.nat_gateways_count = 1
    _configuration.nat_gateway_elastic_address_name_template = f"ea_nat_{_configuration.project_name}" + "_{id}"
    _configuration.nat_gateway_name_template = f"nat_gw_{_configuration.project_name}" + "_{subnet}"

    yield _configuration


@pytest.mark.done
def test_init_environment(configuration):
    assert EnvironmentAPI(configuration, aws_api)


@pytest.mark.done
def test_provision_vpc(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.provision_vpc()


@pytest.mark.done
def test_provision_subnets(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.provision_subnets()


@pytest.mark.todo
def test_provision_bastion(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.provision_bastion()


@pytest.mark.done
def test_provision_internet_gateway(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    inet_gwy = env.provision_internet_gateway()
    assert inet_gwy.id


@pytest.mark.done
def test_provision_public_route_tables(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    inet_gwy = env.provision_internet_gateway()
    route_tables = env.provision_public_route_tables(inet_gwy)
    assert route_tables


@pytest.mark.done
def test_provision_elastic_addresses(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    elastic_addresses = env.provision_elastic_addresses()
    assert elastic_addresses


@pytest.mark.done
def test_provision_nat_gateways(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    elastic_addresses = env.provision_elastic_addresses()
    nat_gateways = env.provision_nat_gateways(elastic_addresses)
    assert nat_gateways


@pytest.mark.done
def test_provision_private_route_tables(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    elastic_addresses = env.provision_elastic_addresses()
    nat_gateways = env.provision_nat_gateways(elastic_addresses)
    route_tables = env.provision_private_route_tables(nat_gateways)
    assert route_tables


@pytest.mark.done
def test_dispose_nat_gateways(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_nat_gateways()


@pytest.mark.done
def test_dispose_elastic_addresses(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.dispose_elastic_addresses()


@pytest.mark.todo
def test_dispose_bastion(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.dispose_bastion()


@pytest.mark.done
def test_dispose_subnets(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.dispose_subnets()


@pytest.mark.done
def test_dispose_route_tables(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_route_tables()


@pytest.mark.done
def test_dispose_internet_gateway(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_internet_gateway()


@pytest.mark.done
def test_dispose_vpc(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.dispose_vpc()


# ECS

@pytest.mark.done
def test_provision_container_instance_security_group(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    sg = env.provision_container_instance_security_group()
    assert sg.id


@pytest.mark.done
def test_provision_container_instance_ssh_key(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    key_pair = env.provision_container_instance_ssh_key()
    assert key_pair.id


@pytest.mark.done
def test_provision_container_instance_launch_template(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    lt = env.provision_container_instance_launch_template()
    assert lt.id


@pytest.mark.done
def test_provision_ecs_cluster(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    ecs_cluster = env.provision_ecs_cluster()
    assert ecs_cluster.arn


@pytest.mark.done
def test_provision_container_instance_auto_scaling_group(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    lt = env.provision_container_instance_launch_template()
    asg = env.provision_container_instance_auto_scaling_group(lt)
    assert asg.arn


@pytest.mark.done
def test_provision_ecs_capacity_provider(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    lt = env.provision_container_instance_launch_template()
    asg = env.provision_container_instance_auto_scaling_group(lt)
    cap_provider = env.provision_ecs_capacity_provider(asg)
    assert cap_provider.arn


@pytest.mark.done
def test_attach_capacity_provider_to_ecs_cluster(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    ecs_cluster = env.provision_ecs_cluster()
    assert env.attach_capacity_provider_to_ecs_cluster(ecs_cluster)


@pytest.mark.done
def test_dispose_ecs_cluster_capacity_provider(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_ecs_cluster_capacity_provider()


@pytest.mark.done
def test_dispose_container_instance_auto_scaling_group(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_container_instance_auto_scaling_group()


@pytest.mark.done
def test_dispose_ecs_cluster(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_ecs_cluster()


@pytest.mark.done
def test_dispose_container_instance_launch_template(configuration):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_container_instance_launch_template()


@pytest.mark.done
def test_dispose_container_instance_ssh_key(configuration):
    """
    Please read the docstring in the function!!!

    :param configuration:
    :return:
    """
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_container_instance_ssh_key()
