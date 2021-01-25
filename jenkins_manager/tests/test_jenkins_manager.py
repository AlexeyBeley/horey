"""
Running tests of several jenkins_manager possibilities.
Not really tests but more like a usage demonstration.
"""
import os
import sys
import datetime


sys.path.insert(0, os.path.abspath("../src"))


from jenkins_manager import JenkinsManager
from jenkins_job import JenkinsJob


qa = {"address": "", "protocol": "http", "port": "8080", "username": "horey", "password": ""}
active = qa
jenkins_manager = JenkinsManager(active["address"], active["username"], active["password"], protocol=active["protocol"], port=active["port"], timeout=60)


def test_cleanup():
    """
    Run the cleanup function and save the output to file.
    :return:
    """
    ret = jenkins_manager.cleanup()
    with open("report.txt", "w+") as fh:
        fh.write(ret)
    print(ret)


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
        print(f"Failed after {datetime.datetime.now()-begin_time} wither error {repr(e)}")
        return

    print(f"Succeed after {datetime.datetime.now() - begin_time}")


def test_trigger_job():
    """
    Trigger single job.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    jenkins_manager.trigger_job(job)


def test_execute_same_job_multiple_times():
    """
    Execute one job multiple times.
    :return:
    """
    report = jenkins_manager.execute_jobs([JenkinsJob("Horey_Test_Project_1", {}, uid_parameter_name="data") for _ in range(10)])
    print(report)


def test_execute_jobs():
    """
    Execute 4 jobs multiple times.
    :return:
    """
    jobs = []
    for i in range(1, 5):
        jobs += [JenkinsJob(f"Horey_Test_Project_{i}", {}, uid_parameter_name="data") for _ in range(10)]
    report = jenkins_manager.execute_jobs(jobs)
    print(report)


def test_get_job_config():
    """
    Test get single job configuration.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    conf_xml = jenkins_manager.get_job_config(job.name)
    print(conf_xml)


def test_save_job_config():
    """
    Test get single job configuration.
    :return:
    """
    job = JenkinsJob("Horey_Test_Project_1", {})
    jenkins_manager.save_job_config(job.name, "./output.txt")


def test_create_jobs():
    """
    Create the jobs to be tested.
    """
    jobs = [JenkinsJob(f"Horey_Test_Project_{i}", {}, uid_parameter_name="data") for i in range(1, 5)]
    for job_ in jobs:
        jenkins_manager.create_job(job_, "job_sample.xml")


def test_delete_jobs():
    """
    Delete the jobs created for tests.
    :return:
    """
    jobs = [JenkinsJob(f"Horey_Test_Project_{i}", {}, uid_parameter_name="data") for i in range(1, 5)]
    jenkins_manager.delete_jobs(jobs)


def test_backup_jobs():
    jenkins_manager.backup_jobs("./backups")


