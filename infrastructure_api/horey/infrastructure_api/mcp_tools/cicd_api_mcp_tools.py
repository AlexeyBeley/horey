"""
MCP tools of horey.infrastructure_api CICDAPI: provision_constructor system functions run on the environment
EC2 instances over SSH (horey.deployer). The SSH keys are the Secrets Manager secrets named as the instances' key pairs.
"""

import contextlib
from typing import Any

from horey.infrastructure_api.cicd_api import CICDAPI
from horey.infrastructure_api.cicd_api_configuration_policy import CICDAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.mcp_tools.base_mcp_tools import BaseMCPTools

# Set by the tool itself, not accepted in the system function parameters.
RESERVED_PARAMETERS = ("s3_deployment_uri", "storage_service")


def generate_s3_deployment_uri(bucket_name: str, path_prefix: str = "") -> str:
    """
    s3://bucket_name/path_prefix, the S3StorageService uri.

    :param bucket_name: e.g. "bucket-horey"
    :param path_prefix: e.g. "deployments/horey"
    :return:
    """

    if not bucket_name or "/" in bucket_name or bucket_name.startswith("s3:"):
        raise ValueError(f"bucket_name must be a bare bucket name, e.g. 'bucket-horey', got: '{bucket_name}'")
    return f"s3://{bucket_name}/{path_prefix.strip('/')}"


class CICDAPIMCPTools(BaseMCPTools):
    """
    CICDAPI tools.
    """

    def cicd_api(self, configuration_name: str | None) -> CICDAPI:
        """
        CICDAPI of the configuration environment.
        """

        return InfrastructureAPI.get_cicd_api(CICDAPIConfigurationPolicy(), self.environment_api(configuration_name))

    # pylint: disable= too-many-arguments, too-many-positional-arguments, too-many-locals
    def register(self) -> None:
        """
        Register the tools.

        :return:
        """

        @self.registry.tool(destructive=True)
        def cicd_run_remote_provision_constructor(instance_name: str, system_function_name: str,
                                                  parameters: dict[str, Any] | None = None,
                                                  bucket_name: str | None = None, bucket_path_prefix: str = "",
                                                  bastion_names: list[str] | None = None,
                                                  ssh_key_secret_name: str | None = None, preserve_status: bool = True,
                                                  windows: bool = False,
                                                  timeout_seconds: int = 60 * 60,
                                                  configuration_name: str | None = None) -> dict[str, Any]:
            """
            Run a provision_constructor system function (e.g. "zabbix", "influxdb", "crowdstrike", "raw") on the
            environment EC2 instance with this Name tag, over SSH; a stopped instance is started first.
            parameters: the system function keyword arguments, e.g. {"action": "install_falcon_sensor"}.
            bucket_name, bucket_path_prefix: S3 directory the system function downloads its files from
            (e.g. installers), needed by "crowdstrike".
            bastion_names: Name tags of the SSH jump hosts, in order: the first by public IP, the next by private IP.
            ssh_key_secret_name: secret holding the instance SSH key, default: the instance key pair name.
            preserve_status: afterwards (also on failure) stop the instance if it was stopped (waits for it,
            about a minute) and delete the downloaded SSH key files that did not exist on the server before.
            Returns the target address, the s3_deployment_uri used and the system function result.
            """
            parameters = dict(parameters or {})
            reserved = [name for name in RESERVED_PARAMETERS if name in parameters]
            if reserved:
                raise ValueError(f"{reserved} are not accepted in parameters, pass bucket_name instead")
            if bucket_path_prefix and not bucket_name:
                raise ValueError("bucket_path_prefix needs bucket_name")
            if bucket_name:
                parameters["s3_deployment_uri"] = generate_s3_deployment_uri(bucket_name, bucket_path_prefix)

            api = self.cicd_api(configuration_name)
            bastions = [api.ec2_api.get_instance(name=bastion_name) for bastion_name in bastion_names or []]
            target_arguments = {"name": instance_name, "target_ssh_key_secret_name": ssh_key_secret_name,
                                "bastions": bastions}
            target_context = (api.deployment_target_preserving_status(**target_arguments) if preserve_status
                              else contextlib.nullcontext(api.generate_deployment_target(**target_arguments)))
            s3_deployment_uri = parameters.get("s3_deployment_uri")
            with target_context as target:
                result = api.run_remote_provision_constructor(target, system_function_name, windows=windows,
                                                              timeout=timeout_seconds, **parameters)
            return {"instance_name": instance_name, "address": target.deployment_target_address,
                    "system_function_name": system_function_name, "s3_deployment_uri": s3_deployment_uri,
                    "preserve_status": preserve_status, "result": self.registry.to_jsonable(result)}
