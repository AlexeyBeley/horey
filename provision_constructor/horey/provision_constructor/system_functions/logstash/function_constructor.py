import pdb
from horey.system_functions.function_base_constructor import FunctionBaseConstructor
import os


class FunctionConstructor(FunctionBaseConstructor):
    def __init__(self, deployment_dir, conf_files, system_d_override_conf_file=None, pipelines_yml_file=None):
        """
        sudo cp logstash/override.conf /etc/systemd/system/logstash.service.d/override.conf
        @param system_d_override_conf_file:
        """
        super().__init__()
        pdb.set_trace()
        function_deployment_dir = os.path.join(deployment_dir, "logstash_system_function")
        function_deployment_data_dir = os.path.join(function_deployment_dir, "data")
        for file_path in conf_files:
            file_name = os.path.basename(file_path)
            pdb.set_trace()
            copy(file_path, os.path.join(function_deployment_data_dir, file_name))



