"""
Logstash service provisioner.

"""


from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.h_logger import get_logger

logger = get_logger()


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Main class.

    """

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)


    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        ret = remoter.execute("touch ~/.hushlogin")
        logger.info(f"Hushlogin: {ret}")
        return True
