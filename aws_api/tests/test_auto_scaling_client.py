"""
Testing AutoScalingClient client.

"""

import os
import pytest
from horey.aws_api.aws_clients.auto_scaling_client import AutoScalingClient
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.aws_api.aws_clients.ecs_client import ECSClient
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup


client = AutoScalingClient()


# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(AutoScalingClient(), AutoScalingClient)


@pytest.mark.skip
def test_detach_instances():
    region = Region.get_region("us-east-1")

    cluster_name = ""
    asg_name = mock_values["autoscaling_group_name_detach_instances_prod"]

    ecs_client = ECSClient()
    ecs_client.clear_cache(None, all_cache=True)
    ret = ecs_client.get_region_container_instances(region, cluster_identifier= cluster_name)
    inst_ids = [x.ec2_instance_id for x in ret if x.status == "DRAINING"]

    asg = AutoScalingGroup({})
    asg.name = asg_name
    asg.region = region
    asg.desired_count = 100
    client.detach_instances(asg, inst_ids, decrement=True)

    ec2_client = EC2Client()
    for inst_id in inst_ids:
        ec2_instance = EC2Instance({})
        ec2_instance.region = region
        ec2_instance.id = inst_id
        ec2_client.dispose_instance(ec2_instance)
