import pdb
import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
#from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Builder(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, pipe_name=None, file_path=None):
        super().__init__(root_deployment_dir, provisioner_script_name, force=force)
        self.add_system_function_common()
        #self.replacement_engine = ReplacementEngine()
        #self.replacement_engine.perform_recursive_replacements(self.deployment_dir,
        #                                                       {"STRING_REPLACEMENT_PIPELINE_NAME": pipe_name,
        #                                                        "STRING_REPLACEMENT_OUTPUT_FILE_NAME": file_path})