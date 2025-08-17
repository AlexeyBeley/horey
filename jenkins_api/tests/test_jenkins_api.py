"""
Running tests of several jenkins_api possibilities.
Not really tests but more like a usage demonstration.
"""
import os
import datetime
import pytest

from horey.jenkins_api.jenkins_api import JenkinsAPI
from horey.jenkins_api.jenkins_job import JenkinsJob
from horey.jenkins_api.jenkins_api_configuration_policy import JenkinsAPIConfigurationPolicy
from horey.jenkins_api.build import Build
from horey.aws_api.aws_api import AWSAPI

ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore")
configuration = JenkinsAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.join(ignore_dir, "jenkins_api_configuration.py")
configuration.region = "il-central-1"

configuration.init_from_file()
jenkins_api = JenkinsAPI(
    configuration, aws_api=AWSAPI()
)


# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_cleanup():
    """
    Run the cleanup function and save the output to file.
    :return:
    """
    ret = jenkins_api.cleanup()
    with open("report.txt", "w+", encoding="utf-8") as fh:
        fh.write(ret)
    print(ret)


@pytest.mark.skip
def test_connection():
    """
    Test the connection to Jenkins.
    :return:
    """
    # Default timeout is: 0:02:31.046387
    begin_time = datetime.datetime.now()
    try:
        print(jenkins_api.server.get_queue_info())
    except Exception as e:
        print(
            f"Failed after {datetime.datetime.now() - begin_time} wither error {repr(e)}"
        )
        return

    print(f"Succeed after {datetime.datetime.now() - begin_time}")


@pytest.mark.skip
def test_execute_same_job_multiple_times():
    """
    Execute one job multiple times.
    :return:
    """
    report = jenkins_api.execute_jobs(
        [
            JenkinsJob("Horey_Test_Project_1", {}, uid_parameter_name="data")
            for _ in range(10)
        ]
    )
    print(report)


@pytest.mark.skip
def test_execute_jobs():
    """
    Execute 4 jobs multiple times.
    :return:
    """
    jobs = []
    for i in range(1, 5):
        jobs += [
            JenkinsJob(f"Horey_Test_Project_{i}", {}, uid_parameter_name="data")
            for _ in range(10)
        ]
    report = jenkins_api.execute_jobs(jobs)
    print(report)


@pytest.mark.skip
def test_get_job_config():
    """
    Test get single job configuration_policy.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    conf_xml = jenkins_api.get_job_config(job.name)
    print(conf_xml)


@pytest.mark.skip
def test_save_job_config():
    """
    Test get single job configuration_policy.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    jenkins_api.save_job_config(job.name, "./output.txt")


@pytest.mark.skip
def test_create_jobs():
    """
    Create the jobs to be tested.
    """
    jobs = [
        JenkinsJob(f"Horey_Test_Project_{i}", {}, uid_parameter_name="data")
        for i in range(1, 5)
    ]
    for job_ in jobs:
        jenkins_api.create_job(job_, "job_sample.xml")


@pytest.mark.skip
def test_delete_jobs():
    """
    Delete the jobs created for tests.
    :return:
    """
    jobs = [
        JenkinsJob(f"Horey_Test_Project_{i}", {}, uid_parameter_name="data")
        for i in range(1, 5)
    ]
    jenkins_api.delete_jobs(jobs)


@pytest.mark.skip
def test_backup_jobs():
    jenkins_api.backup_jobs("./backups")


@pytest.mark.wip
def test_get_all_jobs():
    ret = jenkins_api.get_all_jobs()
    assert isinstance(ret, list)


@pytest.mark.skip
def test_get_job_info():
    jenkins_api.get_job_info("unit_tester")


@pytest.mark.skip
def test_get_build_console_output():
    assert jenkins_api.get_build_console_output("unit_tester", 1)


@pytest.mark.skip
def test_update_build_info():
    build = Build({"name": "unit_tester", "number": 1})
    assert jenkins_api.update_build_info(build)


@pytest.mark.skip
def test_yield_build_logs():
    build = Build({"name": "unit_tester", "number": 1})
    for _ in jenkins_api.yield_build_logs(build):
        pass


@pytest.mark.done
def test_get_running_builds():
    assert isinstance(jenkins_api.get_running_builds(), list)


@pytest.mark.done
def test_get_hagent_subnet_ids():
    jenkins_api.configuration.hagent_subnets_ids = []
    subnets = jenkins_api.get_hagent_subnet_ids()
    assert subnets


@pytest.mark.done
def test_provision_container_instance_security_group():
    jenkins_api.configuration.hagent_subnets_ids = []
    sg = jenkins_api.provision_container_instance_security_group()
    assert sg.id


@pytest.mark.done
def test_generate_hagent_user_data():
    jenkins_api.configuration.hagent_subnets_ids = []
    user_data = jenkins_api.generate_hagent_user_data()
    assert user_data


@pytest.mark.done
def test_provision_container_instance_iam_profile():
    jenkins_api.configuration.hagent_subnets_ids = []
    profile = jenkins_api.provision_container_instance_iam_profile()
    assert profile.arn


@pytest.mark.done
def test_provision_hagent_container_instance_ssh_key():
    jenkins_api.configuration.hagent_subnets_ids = []
    key_pair = jenkins_api.provision_hagent_container_instance_ssh_key()
    assert key_pair.id


@pytest.mark.done
def test_provision_hagent_launch_template():
    jenkins_api.configuration.hagent_subnets_ids = []
    lt = jenkins_api.provision_hagent_launch_template()
    assert lt.id


@pytest.mark.done
def test_provision_hagent_ecs_cluster():
    jenkins_api.configuration.hagent_subnets_ids = []
    cluster = jenkins_api.provision_hagent_ecs_cluster()
    assert cluster.arn


@pytest.mark.done
def test_provision_hagent_auto_scaling_group():
    jenkins_api.configuration.hagent_subnets_ids = []
    launch_template = jenkins_api.provision_hagent_launch_template()
    asg = jenkins_api.provision_hagent_auto_scaling_group(launch_template)
    assert asg.arn


@pytest.mark.done
def test_provision_hagent_ecs_capacity_provider():
    jenkins_api.configuration.hagent_subnets_ids = []
    launch_template = jenkins_api.provision_hagent_launch_template()
    auto_scaling_group = jenkins_api.provision_hagent_auto_scaling_group(launch_template)
    capacity_provider = jenkins_api.provision_hagent_ecs_capacity_provider(auto_scaling_group)
    assert capacity_provider.arn


@pytest.mark.done
def test_attach_hagent_capacity_provider_to_ecs_cluster():
    jenkins_api.configuration.hagent_subnets_ids = []
    cluster = jenkins_api.provision_hagent_ecs_cluster()
    assert jenkins_api.attach_hagent_capacity_provider_to_ecs_cluster(cluster)


@pytest.mark.done
def test_provision_ecs_infra():
    jenkins_api.configuration.hagent_subnets_ids = []
    assert jenkins_api.provision_ecs_infra()
