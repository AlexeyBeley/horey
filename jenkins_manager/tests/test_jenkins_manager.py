"""
Running tests of several jenkins_manager possibilities.
Not really tests but more like a usage demonstration.
"""
import os
import datetime
import pytest

from horey.jenkins_manager.jenkins_manager import JenkinsManager
from horey.jenkins_manager.jenkins_job import JenkinsJob
from horey.jenkins_manager.jenkins_configuration_policy import JenkinsConfigurationPolicy
from horey.jenkins_manager.build import Build

ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore")
configuration = JenkinsConfigurationPolicy()
configuration.configuration_file_full_path = os.path.join(ignore_dir, "jenkins_manager_configuration.py")
configuration.init_from_file()
jenkins_manager = JenkinsManager(
    configuration
)

# pylint: disable= missing-function-docstring

@pytest.mark.skip
def test_cleanup():
    """
    Run the cleanup function and save the output to file.
    :return:
    """
    ret = jenkins_manager.cleanup()
    with open("report.txt", "w+") as fh:
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
        print(jenkins_manager.server.get_queue_info())
    except Exception as e:
        print(
            f"Failed after {datetime.datetime.now()-begin_time} wither error {repr(e)}"
        )
        return

    print(f"Succeed after {datetime.datetime.now() - begin_time}")

@pytest.mark.skip
def test_trigger_job():
    """
    Trigger single job.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    jenkins_manager.trigger_job(job)

@pytest.mark.skip
def test_execute_same_job_multiple_times():
    """
    Execute one job multiple times.
    :return:
    """
    report = jenkins_manager.execute_jobs(
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
    report = jenkins_manager.execute_jobs(jobs)
    print(report)

@pytest.mark.skip
def test_get_job_config():
    """
    Test get single job configuration_policy.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    conf_xml = jenkins_manager.get_job_config(job.name)
    print(conf_xml)

@pytest.mark.skip
def test_save_job_config():
    """
    Test get single job configuration_policy.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    jenkins_manager.save_job_config(job.name, "./output.txt")

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
        jenkins_manager.create_job(job_, "job_sample.xml")

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
    jenkins_manager.delete_jobs(jobs)

@pytest.mark.skip
def test_backup_jobs():
    jenkins_manager.backup_jobs("./backups")

@pytest.mark.skip
def test_get_all_jobs():
    ret = jenkins_manager.get_all_jobs()
    assert isinstance(ret, list)

@pytest.mark.skip
def test_create_user():
    jenkins_manager.create_user("horey", "horeyhorey")

@pytest.mark.skip
def test_get_job_info():
    jenkins_manager.get_job_info("unit_tester")

@pytest.mark.skip
def test_get_build_console_output():
    assert jenkins_manager.get_build_console_output("unit_tester", 1)


@pytest.mark.skip
def test_update_build_info():
    build = Build({"name": "unit_tester", "number": 1})
    assert jenkins_manager.update_build_info(build)

@pytest.mark.skip
def test_yield_build_logs():
    build = Build({"name": "unit_tester", "number": 1})
    for _ in jenkins_manager.yield_build_logs(build):
        pass

@pytest.mark.wip
def test_get_running_builds():
    assert isinstance(jenkins_manager.get_running_builds(), list)
