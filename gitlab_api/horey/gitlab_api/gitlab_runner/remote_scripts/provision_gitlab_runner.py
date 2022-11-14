"""
Agent system functions provisioning script.

"""

# pylint: disable=no-name-in-module
from horey.provision_constructor.provision_constructor import ProvisionConstructor
from horey.h_logger import get_logger

logger = get_logger()

provision_constructor = ProvisionConstructor()


provision_constructor.provision_system_function("ntp")
logger.info("provisioned ntp")
provision_constructor.provision_system_function(
    "apt_package_generic", package_name="curl"
)
logger.info("provisioned curl")

provision_constructor.provision_system_function(
    "horey_package_generic",
    package_name="jenkins_manager",
    horey_repo_path="/home/ubuntu/horey/",
    venv_path="/opt/jenkins_jobs_starter/venv",
)
logger.info("provisioned horey.jenkins_manager")
