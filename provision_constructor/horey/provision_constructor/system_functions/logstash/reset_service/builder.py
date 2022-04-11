import pdb
import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Builder(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, trigger_on_any_provisioned=None):
        pdb.set_trace()
        super().__init__(root_deployment_dir, provisioner_script_name, force=force, trigger_on_any_provisioned=trigger_on_any_provisioned)
        self.add_system_function_common()
        self.replacement_engine = ReplacementEngine()

