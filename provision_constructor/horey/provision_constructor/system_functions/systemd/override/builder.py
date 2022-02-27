import pdb
import os
from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Builder(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, pipe_name=None, filter_file_path=None):
        super().__init__(root_deployment_dir, provisioner_script_name, force=force)
        self.add_system_function_common()
        self.replacement_engine = ReplacementEngine()
        pdb.set_trace()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipe_name}.conf"), "r") as file_handler:
            base_pipeline_conf = file_handler.read()

        comment_line = "#INPUT_BOTOM"
        for pipeline_name in pipeline_names:
            replacement_string = f"- pipeline.id: {pipeline_name}\n" \
                                 f"  path.config: \"\"\n" \
                                  "  pipeline.workers: 1\n\n"

            self.replacement_engine.perform_comment_line_replacement(pipelines_yml_file, comment_line,
                                                                     replacement_string, keep_comment=True)

            pipeline_file = os.path.join(pipelines_dir_path, f"{pipeline_name}.conf")
            with open(pipeline_file, "w") as file_handler:
                file_handler.write(base_pipeline_conf)
