from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine
from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)


@SystemFunctionFactory.register
class Builder(SystemFunctionCommon):
    def __init__(
        self,
        root_deployment_dir,
        provisioner_script_name,
        force=False,
        rotation_path=None,
        file_name=None,
            **kwargs
    ):
        super().__init__(
            root_deployment_dir,
            provisioner_script_name,
            force=force,
            explicitly_add_system_function=False,
            **kwargs
        )
        self.add_system_function_common()

        self.replacement_engine = ReplacementEngine()
        self.replacement_engine.perform_recursive_replacements(
            self.deployment_dir,
            {
                "STRING_REPLACEMENT_ROTATION_PATH": rotation_path,
                "STRING_REPLACEMENT_FILE_NAME": file_name,
            },
        )

        self.add_system_function(force=force)
