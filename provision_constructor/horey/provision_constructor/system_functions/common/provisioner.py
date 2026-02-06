"""
Logstash service provisioner.

"""

import os
from pathlib import Path

from horey.common_utils.remoter import Remoter
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)


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

        if self.action == "ls":
            return self.ls_remote(Path(self.kwargs["path"]))

        raise NotImplementedError(self.action)
