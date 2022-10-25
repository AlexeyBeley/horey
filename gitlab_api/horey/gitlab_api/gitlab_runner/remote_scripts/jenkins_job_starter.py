"""
Jenkins job being authorized and started.
#provision sys.path via ssh
#['/opt/jenkins_jobs_starter', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/home/ubuntu/.local/lib/python3.8/site-packages', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages']


#running sys.path via gitlab runner
#['/opt/jenkins_jobs_starter', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages']

#python3.8 /opt/jenkins_jobs_starter/jenkins_job_starter.py --jenkins_job_json "{\"job_name\":\"1\", \"arguments\":{\"arg_1\":\"val_1\"}, \"identity\":[\"${CI_COMMIT_AUTHOR}\"]}"
 - source /opt/jenkins_jobs_starter/venv/bin/activate && python3.8 /opt/jenkins_jobs_starter/jenkins_job_starter.py --job_name "name" --parameters "{\"arg_1\":\"val_1\"}" --user_identity "{\"CI_COMMIT_AUTHOR\": \"${CI_COMMIT_AUTHOR}\"}"
"""

import json
import argparse
import os

from horey.jenkins_manager.jenkins_manager import JenkinsManager
from horey.jenkins_manager.jenkins_configuration_policy import JenkinsConfigurationPolicy
from horey.jenkins_manager.jenkins_job import JenkinsJob

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_name", type=str)
    parser.add_argument("--parameters", type=str)
    parser.add_argument("--user_identity", type=str)
    configuration_args = parser.parse_args()
    print(json.loads(configuration_args.jenkins_job_json))
    configuration = JenkinsConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                              "jenkins_manager_configuration.py")
    configuration.init_from_file()
    jenkins_manager = JenkinsManager(configuration)
    request = {"job_name": configuration_args.job_name,
               "user_identity": configuration_args.user_identity,
               "parameters": configuration_args.parameters}

    report = jenkins_manager.execute_jobs([JenkinsJob("authenticator", json.dumps({"request": request}),
                                                      uid_parameter_name="data")])
    print(report)
