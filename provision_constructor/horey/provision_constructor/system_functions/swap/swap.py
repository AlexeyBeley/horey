from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Swap(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, swap_size_in_gb=None, ram_size_in_gb=None):
        super().__init__(root_deployment_dir, provisioner_script_name)
        self.swap_size_in_gb = swap_size_in_gb
        self.ram_size_in_gb = ram_size_in_gb

        if self.swap_size_in_gb is None:
            self.init_swap_size_from_ram()

        self.move_system_function_to_deployment_dir()

        replacement_engine = ReplacementEngine()
        replacement_engine.perform_recursive_replacements(self.deployment_dir, {"STRING_REPLACEMENT_SWAP_SIZE_IN_GB":
                                                                                    str(self.ram_size_in_gb)})
        self.add_system_function_to_provisioner_script()

    def init_swap_size_from_ram(self):
        self.swap_size_in_gb = self.ram_size_in_gb * 2


