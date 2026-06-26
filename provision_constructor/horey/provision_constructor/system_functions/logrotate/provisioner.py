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
            overrides = self.kwargs.get("overrides", [])
            postrotate = self.kwargs.get("postrotate")
            return self.add_log_rotation_remote(config_file_name, rotation_paths, overrides, postrotate)
        raise NotImplementedError(self.action)

    def add_log_rotation_remote(self, config_file_name, rotation_paths, overrides, postrotate):
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
            raise NotImplementedError("Multiple users/groups not supported yet")

        user = users[0]
        group = groups[0]
        rotation_path = "\n".join([str(path) for path in rotation_paths]) + "\n"

        composed_file_path = self.compose_config_file(rotation_path, user, group, overrides, postrotate)
        return SystemFunctionFactory.REGISTERED_FUNCTIONS["copy_generic"](self.deployment_dir, self.force, self.upgrade, src=composed_file_path, dst=Path("/etc/logrotate.d")/config_file_name, chmod="640", chown="root:root", sudo=True).provision_remote(
            self.remoter)

    def compose_config_file(self, rotation_paths, user, group, overrides, postrotate):
        """
        Compose logrotate config.

        :param rotation_paths:
        :param user:
        :param group:
        :return:
        """

        su_line = None
        if user != "root" or group != "root":
            su_line = f"    su {user} {group}"

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
                "STRING_REPLACEMENT_ROTATION_PATHS": rotation_paths}
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
        breakpoint()
        return dst_file

