import shutil
import uuid
from pathlib import Path
from tempfile import template

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
            rotation_path = Path(self.kwargs.get("rotation_path"))
            return self.add_log_rotation_remote(config_file_name, rotation_path)
        raise NotImplementedError(self.action)

    def add_log_rotation_remote(self, config_file_name, rotation_path):
        """
        Add log rotation config.

        :return:
        """
        ret = self.remoter.execute(f"sudo stat -c '%U:%G' {rotation_path.parent}")
        user, group = ret[0][-1].split(":")

        composed_file_path = self.compose_config_file(config_file_name, rotation_path, user, group)
        breakpoint()

    def compose_config_file(self, config_file_name, rotation_path, user, group):
        """
        Compose logrotate config.

        :param rotation_path:
        :param config_file_name:
        :param user:
        :param group:
        :return:
        """

        su_line = None
        if user != "root" or group != "root":
            su_line = f"su {user} {group}"

        src = Path(__file__).parent / "templates" / "template_logrotate.conf"
        dst_dir = self.deployment_dir / f"logrotate_provisioner_{uuid.uuid4()}"
        dst_dir.mkdir(exist_ok=False)
        template_dst_file = dst_dir / src.name
        shutil.copyfile(
            src,
            template_dst_file
        )
        ReplacementEngine().perform_recursive_replacements(
            dst_dir,
            {
                "STRING_REPLACEMENT_ROTATION_PATHS": rotation_path}
        )
        dst_file = dst_dir / "logrotate.conf"
        if su_line:
            with open(dst_file, "r", encoding="utf-8") as fh:
                lines = fh.readlines()

            for i, line in enumerate(lines):
                if line.strip() == "}":
                    lines.insert(i, su_line + "\n")
                    break
            else:
                raise ValueError("Was not able to find closing bracket")

            with open(dst_file, "w", encoding="utf-8") as fh:
                fh.writelines(lines)
        return dst_file

