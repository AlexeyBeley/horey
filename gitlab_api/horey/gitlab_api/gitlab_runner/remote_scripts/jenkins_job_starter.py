"""
Jenkins job being authorized and started.
#provision sys.path via ssh
#['/opt/jenkins_jobs_starter', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/home/ubuntu/.local/lib/python3.8/site-packages', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages']


#running sys.path via gitlab runner
#['/opt/jenkins_jobs_starter', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages']

#python3.8 /opt/jenkins_jobs_starter/jenkins_job_starter.py --jenkins_job_json "{\"job_name\":\"1\", \"arguments\":{\"arg_1\":\"val_1\"}, \"identity\":[\"${CI_COMMIT_AUTHOR}\"]}"

"""

import json
import argparse


from horey.jenkins_manager.jenkins_manager import JenkinsManager
from horey.jenkins_manager.jenkins_configuration_policy import JenkinsConfigurationPolicy


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jenkins_job_json", type=str)
    configuration_args = parser.parse_args()
    print(json.loads(configuration_args.jenkins_job_json))
    configuration = JenkinsConfigurationPolicy()
    #configuration.jenkins_host
    #configuration.jenkins_username
    #configuration.jenkins_token
    #configuration.jenkins_protocol
    #configuration.jenkins_port
    #configuration.jenkins_timeout
    jenkins_manager = JenkinsManager(configuration)
