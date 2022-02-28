import pdb
import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Builder(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, any=None):
        super().__init__(root_deployment_dir, provisioner_script_name, force=force)
        self.add_system_function_common()
        self.replacement_engine = ReplacementEngine()
        pdb.set_trace()

