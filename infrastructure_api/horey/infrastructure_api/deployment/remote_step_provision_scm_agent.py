"""
Agent system functions provisioning script.

"""

# pylint: disable=no-name-in-module
from pathlib import Path
from horey.provision_constructor.provision_constructor import ProvisionConstructor
from horey.h_logger import get_logger

logger = get_logger()


def main():
    """
    Provision the ssm_agent.

    :return:
    """

    provision_constructor = ProvisionConstructor()
    provision_constructor.provision_system_function("apt_package_generic", package_names=["all"], force=True,
                                                    upgrade=True)

    horey_repo_path = "/opt/git/horey"
    scm_agent_dir_path = Path("/opt/scm_agent/")

    # Enable provisioners
    provision_constructor.provision_system_function("ntp", upgrade=True)

    provision_constructor.provision_system_function("horey_package_generic",
                                                    package_names=["jenkins_api"],
                                                    horey_repo_path=horey_repo_path, force=True)

    provision_constructor.provision_system_function("copy_generic", src=Path(__file__).parent/"jenkins_api_configuration.json",
                                                    dst=scm_agent_dir_path/"jenkins_api_configuration.json",
                                                    sudo=True,
                                                    owner="ubuntu:ubuntu")

    provision_constructor.provision_system_function("swap", swap_size_in_gb=4)


if __name__ == "__main__":
    main()
