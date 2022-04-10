import pdb
import os
import shutil

from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Builder(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, pipe_name=None, input_file_path=None):
        super().__init__(root_deployment_dir, provisioner_script_name, force=force, explicitly_add_system_function=False)
        self.add_system_function_common()
        self.replacement_engine = ReplacementEngine()
        self.replacement_engine.perform_recursive_replacements(self.deployment_dir,
                                                               {"STRING_REPLACEMENT_PIPELINE_NAME": pipe_name,
                                                                "STRING_REPLACEMENT_INPUT_FILE_PATH": input_file_path})
        pdb.set_trace()
        self.add_system_function(force=force)
