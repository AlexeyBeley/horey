import pdb
import argparse
import json
import sys


sys.path.insert(0, "/Users/alexey.beley/private/horey/environment_bootstrap")

from horey.environment_bootstrap.jenkins.jenkins_deployer import JenkinsDeployer
from horey.environment_bootstrap.jenkins.jenkins_deployer_configuration_policy import JenkinsDeployerConfigurationPolicy
#from horey.jenkins_manager.jenkins_configuration_policy import JenkinsConfigurationPolicy
#from horey.jenkins_manager.jenkins_job import JenkinsJob
from horey.common_utils.actions_manager import ActionsManager

action_manager = ActionsManager()


# region run_job
def deploy_infrastructure_parser():
    description = "Deploy jenkins infra"
    parser = argparse.ArgumentParser(description=description)
    return parser


def deploy_infrastructure(arguments, configs_dict) -> None:
    configuration = JenkinsDeployerConfigurationPolicy()
    configuration.init_from_dictionary(configs_dict)
    configuration.init_from_file()
    jenkins_deployer = JenkinsDeployer(configuration)
    jenkins_deployer.deploy_infrastructure()


action_manager.register_action("deploy_infrastructure", deploy_infrastructure_parser, deploy_infrastructure)
# endregion


if __name__ == "__main__":
    action_manager.call_action(pass_unknown_args=True)
