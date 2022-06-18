import pdb
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.provision_constructor.system_functions.system_function_common import SystemFunctionCommon


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir):
        super().__init__()
        self.deployment_dir = deployment_dir

    def provision(self):
        pdb.set_trace()
        self.init_apt_packages()
