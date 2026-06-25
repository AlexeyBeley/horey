import shutil
from pathlib import Path

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.remoter import Remoter
from horey.replacement_engine.replacement_engine import ReplacementEngine
from horey.provision_constructor.system_function_factory import SystemFunctionFactory


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        super().__init__(deployment_dir, force, upgrade, **kwargs)


    def provision_remote(self, remoter: Remoter):
        """
        Provision logrotate.

        @return:
        """

        self.remoter = remoter

        if self.action == "add_log_rotation":
            config_file_name = self.kwargs.get("config_file_name")
            rotation_paths = self.kwargs.get("rotation_paths")
            return self.add_log_rotation_remote(config_file_name, rotation_paths)
        raise NotImplementedError(self.action)

    def add_log_rotation_remote(self, config_file_name, rotation_paths):
        """
        Add log rotation config.

        :return:
        """
        breakpoint()

        src = Path(__file__).parent / "templates" / "template_logrotate.conf"
        shutil.copyfile(
            src,
            self.deployment_dir/config_file_name,
        )
        ReplacementEngine().perform_recursive_replacements(
            self.deployment_dir,
            {
             "STRING_REPLACEMENT_ROTATION_PATHS": "\n".join(rotation_paths)}
        )

        # todo: place the file



