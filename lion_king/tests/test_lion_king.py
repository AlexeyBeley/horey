"""
Test async orchestrator
"""
import os.path

import pytest

from horey.lion_king.lion_king import LionKing
from horey.lion_king.lion_king_configuration_policy import LionKingConfigurationPolicy

# pylint: disable = missing-function-docstring

configuration_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "lion_king", "lion_king_configuration.py"))


@pytest.mark.done
def test_provision_vpc():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    vpc = lion_king.provision_vpc()
    assert vpc.id


@pytest.mark.done
def test_provision_subnets():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    subnets = lion_king.provision_subnets()
    assert len(subnets) > 0


@pytest.mark.done
def test_provision_ecr_repositories():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    repo = lion_king.provision_ecr_repositories()
    assert repo.arn


@pytest.mark.done
def test_login_to_ecr():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.login_to_ecr()


@pytest.mark.done
def test_prepare_build_directory():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.prepare_build_directory()


@pytest.mark.done
def test_build():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.build()


@pytest.mark.todo
def test_build_and_upload():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.build_and_upload()


@pytest.mark.done
def test_provision_rds_db_cluster_parameter_group():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_rds_db_cluster_parameter_group()


@pytest.mark.done
def test_provision_rds_db_instance_parameter_group():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_rds_db_instance_parameter_group()


@pytest.mark.done
def test_provision_rds_subnet_group():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_rds_subnet_group()


@pytest.mark.done
def test_provision_security_groups():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_security_groups()


@pytest.mark.done
def test_update_component_provision_infra():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.update_component()


@pytest.mark.done
def test_provision_infrastructure():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_infrastructure()


@pytest.mark.done
def test_provision_ecs_cluster():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_ecs_cluster()


@pytest.mark.done
def test_provision_roles():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_roles()


@pytest.mark.done
def test_provision_ecs_task_definition():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_ecs_task_definition()


@pytest.mark.done
def test_provision_ecs_service():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    ecs_cluster = lion_king.provision_ecs_cluster()
    ecs_task_definition = lion_king.provision_ecs_task_definition()
    sec_grps = lion_king.provision_security_groups()
    assert lion_king.provision_ecs_service(ecs_cluster, ecs_task_definition, None, sec_grps[0])


@pytest.mark.done
def test_provision_rds_instance():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_rds_instance()


@pytest.mark.todo
def test_provision_grafana():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_grafana()


@pytest.mark.todo
def test_provision_adminer():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_adminer()


@pytest.mark.done
def test_provision_certificate():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.provision_certificate()


@pytest.mark.wip
def test_provision_routing():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    lion_king.provision_vpc()
    lion_king.provision_subnets()
    assert lion_king.provision_routing()


@pytest.mark.wip
def test_provision_load_balancer_components():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.provision_infrastructure = True
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    lion_king.provision_vpc()
    lion_king.provision_subnets()
    assert lion_king.provision_load_balancer_components()


@pytest.mark.wip
def test_dispose():
    configuration = LionKingConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    lion_king = LionKing(configuration)
    assert lion_king.dispose()
