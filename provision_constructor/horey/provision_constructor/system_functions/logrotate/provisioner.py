import shutil
import uuid
from pathlib import Path
from tempfile import template

from typing_extensions import override

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
            configs = self.kwargs.get("configs")
            return self.add_log_rotation_remote(config_file_name, rotation_paths, configs)
        raise NotImplementedError(self.action)

    def add_log_rotation_remote(self, config_file_name, rotation_paths, configs):
        """
        Add log rotation config.

        :return:
        """
        users = []
        groups = []
        for rotation_path in rotation_paths:
            ret = self.remoter.execute(f"sudo stat -c '%U:%G' {rotation_path.parent}")
            user, group = ret[0][-1].split(":")
            users.append(user)
            groups.append(group)

        users = list(set(users))
        groups = list(set(groups))

        if len(users) > 1 or len(groups) > 1:
            raise NotImplementedError("Multiple users/groups detected for provided paths")

        rotation_path = "\n".join([str(path) for path in rotation_paths]) + "\n"

        composed_file_path = self.compose_config_file(rotation_path, configs)
        return SystemFunctionFactory.REGISTERED_FUNCTIONS["copy_generic"](self.deployment_dir, self.force, self.upgrade, src=composed_file_path, dst=Path("/etc/logrotate.d")/config_file_name, chmod="640", chown="root:root", sudo=True).provision_remote(
            self.remoter)

    def compose_config_file(self, rotation_paths, configs):
        """
        Compose logrotate config.

        :param rotation_paths:
        :param user:
        :param group:
        :return:
        """

        dst_file = self.deployment_dir / f"logrotate_provisioner_{uuid.uuid4()}.conf"
        string_ret = rotation_paths + "\n{"
        string_ret += "    " + "\n    ".join(configs) + "}"
        with open(dst_file, "w", encoding="utf-8") as fh:
            fh.write(string_ret)
        breakpoint()
        return dst_file

    def add_lines_before_close_curly_bracket(self, file_path, new_lines):
        """
        Add line before close curly bracket.

        :param file_path:
        :param new_lines:
        :return:
        """

        with open(file_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()

        for i, line in enumerate(lines):
            if line.strip() == "}":
                for new_line in new_lines:
                    lines.insert(i, new_line + "\n")
                break
        else:
            raise ValueError("Was not able to find closing bracket")

        with open(file_path, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
