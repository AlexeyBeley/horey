import os
import pdb

from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Logstash(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, pipeline_names=None):
        self.replacement_engine = ReplacementEngine()
        super().__init__(root_deployment_dir, provisioner_script_name, force=force)

        self.add_system_function_common()

        self.add_pipelines(pipeline_names)

    def add_pipelines(self, pipeline_names):
        pipelines_dir_path = os.path.join(self.deployment_dir, "pipelines")
        os.makedirs(pipelines_dir_path, exist_ok=True)
        pipelines_yml_file = os.path.join(self.deployment_dir, "pipelines.yml")
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "base_pipeline.conf"), "r") as file_handler:
            base_pipeline_conf = file_handler.read()

        comment_line = "#PIPELINES_BOTOM"
        for pipeline_name in pipeline_names:
            replacement_string = f"- pipeline.id: {pipeline_name}\n" \
                                 f"  path.config: \"/etc/logstash/conf.d/{pipeline_name}.conf\"\n" \
                                  "  pipeline.workers: 1\n\n"

            self.replacement_engine.perform_comment_line_replacement(pipelines_yml_file, comment_line,
                                                                     replacement_string, keep_comment=True)

            pipeline_file = os.path.join(pipelines_dir_path, f"{pipeline_name}.conf")
            with open(pipeline_file, "w") as file_handler:
                file_handler.write(base_pipeline_conf)
