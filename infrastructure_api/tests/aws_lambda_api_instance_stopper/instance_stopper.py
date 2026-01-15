"""
Stops ec2 instances.
"""
import os

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

logger = get_logger()

def handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """

    logger.info(f"Handling {event=}, {context=}")

    aws_api = AWSAPI()

    for instance_id in os.environ["INSTANCE_IDS"].split(","):
        ec2_instance = EC2Instance({})
        ec2_instance.id = instance_id
        ec2_instance.region = Region.get_region(os.environ["REGION"])

        if not aws_api.ec2_client.update_instance_information(ec2_instance):
            raise RuntimeError(f"Can not find instance {instance_id}")

        if ec2_instance.get_state() not in [ec2_instance.State.STOPPED, ec2_instance.State.STOPPING]:
            logger.error(f"Stopping EC2 instance {instance_id} with current State: {ec2_instance.get_state()}")
            aws_api.ec2_client.stop_instance(ec2_instance, asynchronous=True)

    return 200
