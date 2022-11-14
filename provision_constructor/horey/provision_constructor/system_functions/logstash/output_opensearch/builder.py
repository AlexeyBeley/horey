import os
import pdb
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Builder(SystemFunctionFactory.SystemFunction):
    def __init__(
        self,
        root_deployment_dir,
        provisioner_script_name,
        force=False,
        pipe_name=None,
        server_address=None,
        user=None,
        password=None,
        index=None,
    ):
        super().__init__(
            root_deployment_dir,
            provisioner_script_name,
            force=force,
            explicitly_add_system_function=False,
        )
        self.add_system_function_common()
        self.replacement_engine = ReplacementEngine()

        self.replacement_engine.perform_recursive_replacements(
            self.deployment_dir,
            {
                "STRING_REPLACEMENT_PIPELINE_NAME": pipe_name,
                "STRING_REPLACEMENT_OUTPUT_OPENSEARCH_FILE_NAME": "output_opensearch.txt",
                "STRING_REPLACEMENT_OPENSEARCH_ADDRESS": server_address,
                "STRING_REPLACEMENT_INDEX": index,
                "STRING_REPLACEMENT_OPENSEARCH_USERNAME": user,
                "STRING_REPLACEMENT_OPENSEARCH_PASSWORD": password,
            },
        )

        self.add_system_function(force=force)
