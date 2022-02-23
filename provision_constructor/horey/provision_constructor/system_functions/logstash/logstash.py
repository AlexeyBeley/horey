import os
import pdb

from horey.provision_constructor.system_function_factory import SystemFunctionFactory
from horey.replacement_engine.replacement_engine import ReplacementEngine


@SystemFunctionFactory.register
class Logstash(SystemFunctionFactory.SystemFunction):
    def __init__(self, root_deployment_dir, provisioner_script_name, force=False, pipes_names=None):
        self.replacement_engine = ReplacementEngine()
        super().__init__(root_deployment_dir, provisioner_script_name, force=force)

        self.add_system_function_common()

        #self.add_pipeline()

    def add_pipeline(self):
        replacement_string = "- pipeline.id: main\n"\
              "  path.config: \"/etc/logstash/conf.d/main.conf\"\n"\
              "  pipeline.workers: 1\n"

        comment_line = "#PIPELINES_BOTOM"
        pdb.set_trace()
        self.replacement_engine.perform_comment_line_replacement(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                         "pipelines.yaml"), comment_line, replacement_string, keep_comment=True)
