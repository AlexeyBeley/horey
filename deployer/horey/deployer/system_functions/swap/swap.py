import os.path
import pdb

from horey.deployer.system_function_factory import SystemFunctionFactory
from horey.deployer.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Swap(SystemFunctionFactory.SystemFunction):
    def __init__(self, deployment_dir, swap_size_in_gb=None, ram_size_in_gb=None):
        super().__init__(deployment_dir)
        self.swap_size_in_gb = swap_size_in_gb
        self.ram_size_in_gb = ram_size_in_gb

        if self.swap_size_in_gb is None:
            self.init_swap_size_from_ram()

        self.mv_self_to_deployment_dir(os.path.abspath(__file__))

        replacement_engine = ReplacementEngine()
        replacement_engine.perform_recursive_replacements(self.deployment_dir, {"STRING_REPLACEMENT_SWAP_SIZE_IN_GB": str(self.ram_size_in_gb)})
        self.perform_replacements()

    def init_swap_size_from_ram(self):
        self.swap_size_in_gb = self.ram_size_in_gb * 2


