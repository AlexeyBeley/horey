import os
import pdb

from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Logstash(SystemFunctionFactory.SystemFunction):
    def __init__(
        self,
        root_deployment_dir,
        provisioner_script_name,
        force=False,
        pipeline_names=None,
    ):
        self.replacement_engine = ReplacementEngine()
        super().__init__(root_deployment_dir, provisioner_script_name, force=force)

        self.add_system_function_common()
