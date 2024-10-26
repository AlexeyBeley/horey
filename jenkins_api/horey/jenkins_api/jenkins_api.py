"""
Module to handle jenkins server.
"""
import copy
import json
import os
import datetime
import time
import threading
from collections import defaultdict
import jenkins
import requests
from horey.jenkins_api.node import Node
from horey.jenkins_api.jenkins_job import JenkinsJob
from horey.jenkins_api.build import Build
from horey.h_logger import get_logger
from horey.aws_api.base_entities.region import Region
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup
from horey.aws_api.aws_services_entities.ecs_capacity_provider import ECSCapacityProvider
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.key_pair import KeyPair
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster

logger = get_logger()


def retry_on_errors(exceptions_to_catch, count=12, timeout=5):
    """
    Decorator to catch errors against Jenkins server and perform retries.

    :param exceptions_to_catch:
    :param count:
    :param timeout:
    :return:
    """

    def func_wrapper(base_func):
        """
        Wrap the function.

        :param base_func:
        :return:
        """

        def func_base(*args, **kwargs):
            """
            Caller.

            :param args:
            :param kwargs:
            :return:
            """

            for i in range(count):
                try:
                    return base_func(*args, **kwargs)
                except exceptions_to_catch:
                    logger.info(
                        f"{base_func.__name__} failed, retry {i}/{count} after {timeout} seconds"
                    )
                time.sleep(timeout)
            raise TimeoutError(f"count: {count} timeout: {timeout}")

        return func_base

    return func_wrapper


class JenkinsAPI:
    """
    Perform several tasks against Jenkins server.
    Main task- trigger multiple jobs and follow their execution.
    """

    JOBS_START_TIMEOUT = 20 * 60
    JOBS_FINISH_TIMEOUT = 20 * 60
    SLEEP_TIME = 5
    BUILDS_PER_JOB = defaultdict(lambda: defaultdict(lambda: None))

    def __init__(self, configuration, aws_api=None):
        self.configuration = configuration

        self.server = jenkins.Jenkins(
            configuration.host,
            username=configuration.username,
            password=configuration.token,
            timeout=configuration.timeout,
        )
        self.aws_api = aws_api
        if self.aws_api:
            AWSAccount.set_aws_default_region(self.region)
        self._vpc = None

    @property
    def hostname(self):
        """
        Fetch from host

        :return:
        """

        raise NotImplementedError()

    def execute_jobs(self, jobs):
        """
        Function to trigger a flow of multiple jobs' execution. At the end prints the failed jobs.
        :param jobs:
        :return:
        """

        self.set_jobs_current_builds(jobs)
        self.trigger_jobs(jobs)
        self.wait_for_builds_to_start_execution(jobs)
        self.wait_for_builds_to_finish_execution(jobs)
        return self.report_results(jobs)

    def set_jobs_current_builds(self, jobs):
        """
        Set current build_ids for all jobs.
        They will be used as a baseline for searching the build_its-
        since the build_id is incrementing no way it will be less than this number.
        :param jobs:
        :return:
        """
        for job in jobs:
            if job.name not in self.BUILDS_PER_JOB:
                self.BUILDS_PER_JOB[job.name][
                    self.get_next_build_number(job.name)
                ] = None

    def trigger_jobs(self, jobs, multithreaded=True):
        """
        Trigger all jobs.
        :param jobs:
        :param multithreaded: If True- triggers each job in a separate thread.
        :return:
        """
        start_time = datetime.datetime.now()
        logger.info("Begin triggering jobs")
        for job in jobs:
            if multithreaded:
                single_job_thread = threading.Thread(
                    target=self.thread_trigger_job, args=(job,)
                )
                single_job_thread.start()
            else:
                self.thread_trigger_job(job)

        logger.info(
            f"Finished triggering jobs took {datetime.datetime.now() - start_time}"
        )

    @retry_on_errors((requests.exceptions.ConnectionError,), count=12, timeout=5)
    def thread_trigger_job(self, job: JenkinsJob):
        """
        Function to trigger single job.
        :param job:
        :return:
        """
        parameters = job.get_request_parameters()
        logger.info(f"Triggering job {job.name} with parameters {parameters}")
        queue_item_id = self.server.build_job(job.name, parameters=parameters)
        job.queue_item_id = queue_item_id
        logger.info(f"Triggered job with queue_id: {queue_item_id}")

    def wait_for_builds_to_start_execution(self, jobs):
        """
        Wait for triggered jobs to exit the waiting queue and start execution.
        :param jobs:
        :return:
        """
        start_time = datetime.datetime.now()

        while (
            any(job.build_id is None for job in jobs)
            and (datetime.datetime.now() - start_time).seconds < self.JOBS_START_TIMEOUT
        ):

            for job in jobs:
                if job.queue_item_id is None:
                    continue

                if job.build_id is not None:
                    continue

                try:
                    self.update_job_build_id_by_queue_id(job)
                except jenkins.JenkinsException as exception_received:
                    if f"queue number[{job.queue_item_id}] does not exist" not in repr(
                        exception_received
                    ):
                        raise
                    logger.info(
                        f"Queue item '{job.queue_item_id}' does not exist anymore updating with parameter"
                    )
                    self.update_job_build_id_by_parameter_uid(job)

            if all(job.build_id is not None for job in jobs):
                break

            logger.info(
                f"wait_for_builds_to_start_execution going to sleep for: {self.SLEEP_TIME}"
            )
            time.sleep(self.SLEEP_TIME)

    @retry_on_errors((requests.exceptions.ConnectionError,), count=12, timeout=5)
    def update_job_build_id_by_queue_id(self, job):
        """
        Find the build Id based on queue item Id.
        :param job:
        :return:
        """
        dict_item = self.server.get_queue_item(job.queue_item_id)
        if "executable" in dict_item:
            job.build_id = dict_item["executable"].get("number")

    @retry_on_errors((requests.exceptions.ConnectionError,), count=12, timeout=5)
    def update_job_build_id_by_parameter_uid(self, job):
        """
        If the queue item was already deleted use the parameter uid to find the build in the history.
        :param job:
        :return:
        """
        if job.uid_parameter_name is None:
            return

        start_build_id = min(list(self.BUILDS_PER_JOB[job.name].keys()))
        end_build_id = self.get_next_build_number(job.name) - 1

        for build_id in range(end_build_id, start_build_id, -1):
            if self.BUILDS_PER_JOB[job.name][build_id] is None:
                self.update_build_status(job.name, build_id)

            uid_parameter_value = self.get_uid_parameter_value_from_build_info(
                self.BUILDS_PER_JOB[job.name][build_id], job.uid_parameter_name
            )
            if job.uid == uid_parameter_value:
                job.build_id = build_id
                logger.info(f"Found build uid {build_id}")
                break

    @staticmethod
    def get_uid_parameter_value_from_build_info(build_info, uid_parameter_name):
        """
        Extract the uid_parameter value from build info response.
        :param build_info:
        :param uid_parameter_name:
        :return:
        """
        for action in build_info["actions"]:
            if action["_class"] == "hudson.model.ParametersAction":
                for parameter in action["parameters"]:
                    if parameter["name"] == uid_parameter_name:
                        return parameter["value"]
        return None

    def wait_for_builds_to_finish_execution(self, jobs):
        """
        Wait for all jobs to reach any final status - success, unstable, aborted, failed
        :param jobs:
        :return:
        """
        start_time = datetime.datetime.now()
        while (
            any(job.build_status is None for job in jobs)
        ):
            passed_time = (datetime.datetime.now() - start_time).seconds
            if passed_time >= self.JOBS_FINISH_TIMEOUT:
                raise TimeoutError(f"Reached timeout while waiting for jobs completion: {[job.build_status for job in jobs]}")

            try:
                self.update_builds_statuses(jobs)
            except jenkins.JenkinsException as jenkins_error:
                repr_jenkins_error = repr(jenkins_error)
                if (
                    "number[" not in repr_jenkins_error
                    or "does not exist" not in repr_jenkins_error
                ):
                    logger.info(
                        f"wait_for_builds_to_finish_execution waits for jobs to start execution {repr_jenkins_error}"
                    )
                    raise

            if all(job.build_status is not None for job in jobs):
                break

            logger.info(
                f"Waitig for builds to finish execution. Going to sleep for: {self.SLEEP_TIME} sec, {passed_time}/{self.JOBS_FINISH_TIMEOUT}"
            )

            time.sleep(self.SLEEP_TIME)

    def update_builds_statuses(self, jobs):
        """
        Fetch new builds' statuses for running builds.
        :param jobs:
        :return:
        """
        for job in jobs:
            if job.build_status is not None:
                continue
            if job.build_id is None:
                continue

            job.build_status = self.update_build_status(job.name, job.build_id)
            if job.build_status is not None:
                logger.info(
                    f"Finished execution build_id: {job.build_id} with result: {job.build_status}"
                )

    @retry_on_errors((requests.exceptions.ConnectionError,), count=12, timeout=5)
    def update_build_status(self, job_name, build_id):
        """
        Fetch single build status from Jenkins.
        :param job_name:
        :param build_id:
        :return:
        """
        logger.info(f"Updating build status for job: {job_name} build_id: {build_id}")
        build_info = self.server.get_build_info(job_name, build_id)
        self.BUILDS_PER_JOB[job_name][build_id] = build_info

        build_status = build_info.get("result")

        return build_status

    @retry_on_errors((requests.exceptions.ConnectionError,), count=12, timeout=5)
    def get_job_info(self, job_name):
        """
        Fetch single job's information from Jenkins.

        :param job_name:
        :return:
        """
        job_info = self.server.get_job_info(job_name)

        return job_info

    def get_next_build_number(self, job_name):
        """
        Get the next build number for a specific job.
        :param job_name:
        :return:
        """
        job_info = self.get_job_info(job_name)
        return job_info["nextBuildNumber"]

    def report_results(self, jobs):
        """
        Generate report for finished jobs.
        :param jobs:
        :return:
        """
        report_lines = []
        for job in jobs:
            if job.build_status is None:
                if job.build_id is None:
                    line = f"Error: Job failed to start job: '{job.name}': {job.get_request_parameters()}"
                    report_lines.append(line)
                    continue
                line = f"Error: Waiting timeout reached job: '{job.name}': {self.BUILDS_PER_JOB[job.name][job.build_id]['url']}"
                report_lines.append(line)
            elif job.build_status not in ["SUCCESS"]:
                line = f"Error: Job: '{job.name}' failed to finish [{job.build_status}]: {self.BUILDS_PER_JOB[job.name][job.build_id]['url']}"
                report_lines.append(line)
                continue
        return "\n".join(report_lines)

    def get_job_config(self, job_name):
        """
        Fetch job's configuration_policy. XML string returned
        :param job_name:
        :return:
        """
        str_job_xml = self.server.get_job_config(job_name)
        return str_job_xml

    def save_job_config(self, job_name, file_output):
        """
        Fetch job's configuration_policy and save it to file.
        :param job_name:
        :param file_output:
        :return:
        """
        try:
            str_job_xml = self.get_job_config(job_name)
        except jenkins.NotFoundException as exception_received:
            logger.error(repr(exception_received))
            return

        with open(file_output, "w+", encoding="utf-8") as file_handler:
            file_handler.write(str_job_xml)

    @retry_on_errors((requests.exceptions.HTTPError,), count=12, timeout=5)
    def create_job(self, job, file_input, overwrite=False):
        """
        Create a job with specific name and xml configs file.
        :param job:
        :param file_input:
        :param overwrite:
        :return:
        """
        with open(file_input, encoding="utf-8") as file_handler:
            str_job_xml = file_handler.read()

        logger.info(f"Starting job creation {job.name} from {file_input}")
        try:
            self.server.create_job(job.name, str_job_xml)
        except jenkins.JenkinsException as exception_received:
            if f"job[{job.name}] already exists" not in repr(exception_received):
                raise
            logger.info(repr(exception_received))
            if overwrite:
                self.delete_jobs([job])
                self.server.create_job(job.name, str_job_xml)
        logger.info(f"Created job {job.name} from {file_input}")

    def create_jobs(self, backups_dir, jobs_names, overwrite=False):
        """
        Create from backups

        :param backups_dir:
        :param jobs_names:
        :param overwrite:
        :return:
        """

        logger.info(f"Creating jobs from  '{backups_dir}': {jobs_names}")

        if len(jobs_names) != 1:
            raise NotImplementedError("todo:")

        for file_name in os.listdir(backups_dir):
            if not file_name.endswith(".xml"):
                continue

            job_name = file_name[: -len(".xml")]
            if job_name not in jobs_names:
                continue

            job = JenkinsJob(job_name, {})
            self.create_job(
                job, os.path.join(backups_dir, file_name), overwrite=overwrite
            )

    @retry_on_errors((requests.exceptions.HTTPError,), count=12, timeout=5)
    def delete_jobs(self, jobs):
        """
        Delete jobs - ignore not existing jobs.
        :param jobs:
        :return:
        """
        for job in jobs:
            logger.info(f"Deleting job {job.name}")
            try:
                self.server.delete_job(job.name)
            except jenkins.NotFoundException as exception_received:
                logger.info(repr(exception_received))

    # pylint: disable = too-many-locals
    def cleanup(self, output_file=None):
        """
        Bonus function - if you get many dirty jobs (qa/stg) this function can help you.
        1) Jobs not being executed for 30 days or more.
        2) Jobs with 100 last failed executions.

        :return:
        """
        jobs = self.get_all_jobs()
        now = datetime.datetime.now()
        time_limit = datetime.timedelta(days=30)
        lst_ret = []
        lst_ret_exceeded_time = []
        for job in jobs:
            try:
                job_info = self.get_job_info(job["name"])
            except jenkins.JenkinsException as exception_received:
                if "does not exist" in repr(exception_received):
                    lst_ret.append(repr(exception_received))
                    continue
                raise

            last_build = job_info.get("lastBuild")
            if last_build is None:
                lst_ret.append(f"{job['name']}: Never run")
                continue

            build_info = self.server.get_build_info(job["name"], last_build["number"])
            last_build_date = datetime.datetime.fromtimestamp(
                build_info["timestamp"] / 1000
            )
            if now - last_build_date > time_limit:
                report_line = f"{job['name']}: last_build_date {(now - last_build_date).days} days ago"
                lst_ret_exceeded_time.append(
                    (report_line, (now - last_build_date).days)
                )
            else:
                for build in job_info["builds"]:
                    self.update_build_status(job["name"], build["number"])
                    if (
                        self.BUILDS_PER_JOB[job["name"]][build["number"]]["result"]
                        == "SUCCESS"
                    ):
                        break
                else:
                    lst_ret.append(
                        f"{job['name']}: last {len(job_info['builds'])} builds were not SUCCESS"
                    )

        lst_ret = [
            x[0]
            for x in sorted(lst_ret_exceeded_time, key=lambda x: x[1], reverse=True)
        ] + lst_ret
        report = "\n".join(lst_ret)
        if output_file:
            with open(output_file, "w+", encoding="utf-8") as file_handler:
                file_handler.write(report)

        return report

    @retry_on_errors((requests.exceptions.ConnectionError,), count=12, timeout=5)
    def get_all_jobs(self):
        """
        Get all jobs' overview information.
        :return:
        """
        job_dicts = self.server.get_all_jobs()
        return job_dicts

    def backup_jobs(self, backups_dir, jobs_names=None):
        """
        Save all jobs' configs in separate files.

        :param backups_dir:
        :param jobs_names:
        :return:
        """
        os.makedirs(backups_dir, exist_ok=True)

        backup_dir_name = self.hostname.replace(".", "_")
        backup_dir_path = os.path.join(backups_dir, backup_dir_name)
        os.makedirs(backup_dir_path, exist_ok=True)
        for job in self.get_all_jobs():
            if jobs_names is not None and job["name"] not in jobs_names:
                continue

            logger.info(f"Start backing up job {job['name']}")
            self.save_job_config(
                job["name"], os.path.join(backup_dir_path, f"{job['name']}.xml")
            )
            logger.info(f"End backing up job '{job['name']}'")

    @staticmethod
    def load_job_names_from_file(jobs_file_path):
        """
        Old and have no idea

        :param jobs_file_path:
        :return:
        """

        with open(jobs_file_path, encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        return [line.strip() for line in lines]

    def disable_jobs_from_file(self, jobs_file_path):
        """
        Old and have no idea

        :param jobs_file_path:
        :return:
        """

        for job_name in self.load_job_names_from_file(jobs_file_path):
            logger.info(f"Disabling job: '{job_name}'")
            self.server.disable_job(job_name)

    def delete_jobs_from_file(self, jobs_file_path):
        """
        Old and have no idea

        :param jobs_file_path:
        :return:
        """

        jobs = [
            JenkinsJob(
                job_name,
                {},
            )
            for job_name in self.load_job_names_from_file(jobs_file_path)
        ]
        self.delete_jobs(jobs)

    def find_build(self, jobs_names, search_string):
        """
        Find builds including a search string in their configuration.

        :param jobs_names:
        :param search_string:
        :return:
        """

        for job_name in jobs_names:
            job_info = self.get_job_info(job_name)
            for build in job_info["builds"]:
                self.update_build_status(job_name, build["number"])
                if (
                    str(self.BUILDS_PER_JOB[job_name][build["number"]]).find(
                        search_string
                    )
                    > -1
                ):
                    logger.info(
                        f"Found in Job: '{job_name}' Build: '{build['number']}'"
                    )

    def get_build_console_output(self, job, start_offset=0):
        """
        Many thanks to:
        https://github.com/arangamani/jenkins_api_client


        get_msg = "/job/#{path_encode job_name}/#{build_num}/logText/progressive#{mode}?"
        get_msg << "start=#{start}"
        progressiveText / progressiveHTML
        url =  self.server._build_url(request_sub_url)
        response = self.server.jenkins_open(requests.Request("GET", url))

        :param job:
        :return:
        """

        logger.info(f"Fetching console output for {job.name=}, {job.build_id=}")
        request_sub_url = f"job/{job.name}/{job.build_id}/logText/progressiveText?start={start_offset}"
        return self.get(request_sub_url)

    @retry_on_errors((requests.exceptions.ConnectionError, jenkins.TimeoutException), count=12, timeout=5)
    def get(self, request_sub_url):
        """
        Run GET.
        https://www.postman.com/api-evangelist/workspace/jenkins/request/18795395-655e1dfd-9dd0-44c5-aa1e-7bbeadbfb065

        :param request_sub_url:
        :return:
        """
        url = self.server._build_url(request_sub_url)
        response = self.server.jenkins_open(requests.Request("GET", url))

        if not response:
            raise ValueError(f"Was not able to extract data: '{response}'")
        return response

    @retry_on_errors((requests.exceptions.ConnectionError, jenkins.TimeoutException), count=12, timeout=5)
    def update_build_info(self, build):
        """
        Update_build info.

        :param build:
        :return:
        """

        try:
            build_info = self.server.get_build_info(build.name, build.number)
        except jenkins.JenkinsException as exception_received:
            if "does not exist" not in repr(
                    exception_received
            ):
                raise
            return False

        build.update_from_raw_response(build_info)
        return True

    def yield_build_logs(self, build, timeout=5):
        """
        Yield log chunks received from running build

        :param build:
        :param timeout:
        :return:
        """

        full_log = ""
        while not build.finished:
            new_full_log = self.get_build_console_output(build)
            if full_log != new_full_log:
                log_chunk = new_full_log[len(full_log):]
                chunk_log_lines = log_chunk.split("\n")
                if len(chunk_log_lines) < 2:
                    log_line_to_print = "\n".join(chunk_log_lines)
                else:
                    log_line_to_print = chunk_log_lines[-2]
                logger.info(f"LOG LINE >>> {log_line_to_print}")
                yield log_chunk
                self.update_build_info(build)
                full_log = new_full_log

            logger.info(f"Fetching build {build.number} logs. Going to sleep {timeout=} seconds")
            time.sleep(timeout)

        return full_log

    def get_running_builds(self):
        """
        Get all active builds.

        :return:
        """

        busy_executors = self.find_busy_executors()
        return [Build(busy_executor["currentExecutable"]) for busy_executor in busy_executors]

    def get_nodes(self, update_info=False, depth=1):
        """
        Fetch nodes data.

        :return:
        """

        cache_file_name = f"computer_depth_{depth}"
        if update_info:
            response = self.get(f"computer/api/json?depth={depth}")
            self.cache(cache_file_name, response)
            dict_src = json.loads(response)
        else:
            dict_src = self.load_from_cache(cache_file_name)
            if dict_src is None:
                return self.get_nodes(update_info=True, depth=depth)

        nodes = [Node(computer_src) for computer_src in dict_src["computer"]]

        return nodes

    def cache(self, file_name, cache_obj):
        """
        Cache response.

        :return:
        """
        if not isinstance(cache_obj, str):
            cache_obj = json.dumps(cache_obj)

        with open(os.path.join(self.configuration.cache_dir_path, file_name), "w", encoding="utf-8") as file_handler:
            file_handler.write(cache_obj)

    def load_from_cache(self, file_name):
        """
        Cache response.

        :return:
        """

        file_path = os.path.join(self.configuration.cache_dir_path, file_name)
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as file_handler:
            return json.load(file_handler)

    def find_busy_executors(self, depth=2):
        """
        Find busy executors.

        :return:
        """

        lst_ret = []
        for node in self.get_nodes(update_info=True, depth=depth):
            for executor in node.executors:
                if executor["idle"]:
                    continue
                lst_ret.append(executor)

        return lst_ret

    @property
    def region(self):
        """
        Object getter

        :return:
        """

        return Region.get_region(self.configuration.region)

    @property
    def vpc(self):
        """
        Object getter

        :return:
        """
        if self._vpc is None:
            filters = [{
                "Name": "tag:Name",
                "Values": [
                    self.configuration.vpc_name
                ]
            }]

            vpcs = self.aws_api.ec2_client.get_region_vpcs(self.region, filters=filters)
            if len(vpcs) > 1:
                raise RuntimeError(f"Found more then 1 vpc by filters {filters}")

            if len(vpcs) == 1:
                self._vpc = vpcs[0]
            else:
                raise RuntimeError(f"Was not able to find VPC: {filters}")

        return self._vpc

    @vpc.setter
    def vpc(self, value):
        """
        Object getter

        :return:
        """

        self._vpc = value

    def provision_ecs_infra(self):
        """
        AWS infra.

        :return:
        """
        self.environment.provision()
        breakpoint()

        self.provision_ecr_repositories()
        self.provision_container_instance_security_group()
        self.provision_hagent_container_instance_ssh_key()
        launch_template = self.provision_hagent_launch_template()
        ecs_cluster = self.provision_hagent_ecs_cluster()
        auto_scaling_group = self.provision_hagent_auto_scaling_group(launch_template)
        self.provision_hagent_ecs_capacity_provider(auto_scaling_group)

        self.attach_hagent_capacity_provider_to_ecs_cluster(ecs_cluster)
        return True
        # self.update_hagent_auto_scaling_group_desired_count(auto_scaling_group)


    def provision_ecr_repositories(self):
        """
        All ECR repos used in the project.

        :return:
        """
        breakpoint()
        for name in [self.configuration.ecr_repository_backend_name,
                     self.configuration.ecr_repository_adminer_name,
                     self.configuration.ecr_repository_grafana_name]:
            self.provision_ecr_repository(name)
        return True

    def provision_ecr_repository(self, repo_name):
        """
        Create or update the ECR repo

        :return:
        """
        breakpoint()
        repo = ECRRepository({})
        repo.region = self.region
        repo.name = repo_name
        repo.tags = copy.deepcopy(self.tags)
        repo.tags.append({
            "Key": "Name",
            "Value": repo.name
        })

        repo.tags.append({
            "Key": self.configuration.infrastructure_last_update_time_tag,
            "Value": datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        })
        self.aws_api.provision_ecr_repository(repo)
        return repo

    def provision_internet_gateway(self):
        """
        Provision the main public router - gateway to the internet.

        :return:
        """
        breakpoint()
        inet_gateway = InternetGateway({})
        inet_gateway.attachments = [{"VpcId": self.vpc.id}]
        inet_gateway.region = self.region
        inet_gateway.tags = copy.deepcopy(self.tags)
        inet_gateway.tags.append({
            "Key": "Name",
            "Value": self.configuration.internet_gateway_name
        })

        self.aws_api.provision_internet_gateway(inet_gateway)

        return inet_gateway

    def provision_public_route_tables(self, internet_gateway):
        """
        Public subnets route tables.

        :param internet_gateway:
        :return:
        """
        breakpoint()
        public_subnets = [subnet for subnet in self.subnets if "public" in subnet.get_tagname()]
        # public
        for public_subnet in public_subnets:
            route_table = RouteTable({})
            route_table.region = self.region
            route_table.vpc_id = self.vpc.id
            route_table.associations = [{
                "SubnetId": public_subnet.id
            }]

            route_table.routes = [{
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": internet_gateway.id
            }]

            route_table.tags = copy.deepcopy(self.tags)
            route_table.tags.append({
                "Key": "Name",
                "Value": self.configuration.route_table_template.format(public_subnet.get_tagname())
            })

            self.aws_api.provision_route_table(route_table)

    def provision_container_instance_security_group(self):
        """
        Provision the container instance security group.

        :return:
        """

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.vpc.id
        security_group.name = self.configuration.hagent_security_group_name
        security_group.description = "Hagent container instance"
        security_group.region = self.region
        security_group.tags = self.configuration.tags
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

        self.aws_api.provision_security_group(security_group, provision_rules=False)

        return security_group

    def provision_hagent_container_instance_ssh_key(self):
        """
        Standard.

        :return:
        """

        key_pair = KeyPair({})
        key_pair.name = self.configuration.hagent_container_instance_ssh_key_pair_name
        key_pair.key_type = "ed25519"
        key_pair.region = self.region
        key_pair.tags = self.configuration.tags 
        key_pair.tags.append({
            "Key": "Name",
            "Value": key_pair.name
        })

        self.aws_api.provision_key_pair(key_pair, save_to_secrets_manager=True,
                                        secrets_manager_region=Region.get_region(self.configuration.secrets_manager_region))

        return key_pair

    def provision_hagent_launch_template(self):
        """
        Provision hagent container instance launch template.

        :return:
        """

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                                            self.configuration.hagent_security_group_name)

        param = self.aws_api.ssm_client.get_region_parameter(self.region,
                                            "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended")

        filter_request = {"ImageIds": [json.loads(param.value)["image_id"]]}
        amis = self.aws_api.ec2_client.get_region_amis(self.region, custom_filters=filter_request)
        if len(amis) > 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")

        ami = amis[0]
        user_data = self.generate_hagent_user_data()

        launch_template = EC2LaunchTemplate({})
        launch_template.name = self.configuration.hagent_container_instance_launch_template_name
        launch_template.region = self.region
        launch_template.tags = self.configuration.tags
        launch_template.tags.append({
            "Key": "Name",
            "Value": launch_template.name
        })
        launch_template.launch_template_data = {"EbsOptimized": False,
                                                "IamInstanceProfile": {
                                                    "Arn": self.provision_container_instance_iam_profile().arn
                                                },
                                                "BlockDeviceMappings": [
                                                    {
                                                        "DeviceName": "/dev/xvda",
                                                        "Ebs": {
                                                            "VolumeSize": 30,
                                                            "VolumeType": "gp3"
                                                        }
                                                    }
                                                ],
                                                "ImageId": ami.id,
                                                "InstanceType": "c5.large",
                                                "KeyName": self.configuration.hagent_container_instance_ssh_key_pair_name,
                                                "Monitoring": {
                                                    "Enabled": False
                                                },
                                                "NetworkInterfaces": [
                                                    {
                                                        "AssociatePublicIpAddress": False,
                                                        "DeleteOnTermination": True,
                                                        "DeviceIndex": 0,
                                                        "Groups": [
                                                            security_group.id,
                                                        ]
                                                    },
                                                ],
                                                "UserData": user_data
                                                }
        self.aws_api.provision_launch_template(launch_template)
        return launch_template
    
    def get_hagent_subnet_ids(self):
        """
        Find private subnets in the VPC

        :return: 
        """

        if self.configuration.hagent_subnets_ids:
            return self.configuration.hagent_subnets_ids

        filters = [{"Name": "vpc-id", "Values": [self.vpc.id]}]
        subnets = self.aws_api.ec2_client.get_region_subnets(self.region, filters=filters)
        if len(subnets) == 0:
            raise ValueError(f"Can not find subnets in region '{self.region.region_mark}' by filter {filters}")

        return [subnet for subnet in subnets if
                    "private" in subnet.get_tagname()]

    def provision_hagent_auto_scaling_group(self, launch_template):
        """
        Provision the container instance auto-scaling group.

        :param launch_template:
        :return:
        """

        as_group = AutoScalingGroup({})
        as_group.name = self.configuration.hagent_container_instance_auto_scaling_group_name
        as_group.region = self.region
        region_objects = self.aws_api.autoscaling_client.get_region_auto_scaling_groups(as_group.region,
                                                                                        names=[as_group.name])

        if len(region_objects) > 1:
            raise RuntimeError(f"more there one as_group '{as_group.name}'")

        if region_objects and region_objects[0].get_status() == region_objects[0].Status.ACTIVE:
            as_group.desired_capacity = 1
            as_group.min_size = 1
        else:
            # was 0
            as_group.min_size = 1
            as_group.desired_capacity = 1

        as_group.tags = self.configuration.tags
        as_group.tags.append({
            "Key": "Name",
            "Value": as_group.name
        })
        as_group.launch_template = {
            "LaunchTemplateId": launch_template.id,
            "Version": "$Default"
        }
        as_group.max_size = self.configuration.hagent_container_instance_auto_scaling_group_max_size
        as_group.default_cooldown = 300

        as_group.health_check_type = "EC2"
        as_group.health_check_grace_period = 300
        as_group.vpc_zone_identifier = ",".join([subnet.id for subnet in self.get_hagent_subnet_ids()])
        as_group.termination_policies = [
            "Default"
        ]
        as_group.new_instances_protected_from_scale_in = False
        as_group.service_linked_role_arn = f"arn:aws:iam::{self.aws_api.ec2_client.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"
        self.aws_api.provision_auto_scaling_group(as_group)
        return as_group

    def provision_hagent_ecs_cluster(self):
        """
        Provision the ECS cluster for this env.

        :return:
        """

        cluster = ECSCluster({})
        cluster.settings = [
            {
                "name": "containerInsights",
                "value": "enabled"
            }
        ]
        cluster.name = self.configuration.hagent_cluster_name
        cluster.region = self.region
        cluster.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.configuration.tags]
        cluster.tags.append({
            "key": "Name",
            "value": cluster.name
        })
        cluster.configuration = {}

        self.aws_api.provision_ecs_cluster(cluster)
        return cluster

    def provision_hagent_ecs_capacity_provider(self, auto_scaling_group):
        """
        Create capacity provider from provision instances.

        :param auto_scaling_group:
        :return:
        """
        capacity_provider = ECSCapacityProvider({})
        capacity_provider.name = self.configuration.hagent_container_instance_capacity_provider_name
        capacity_provider.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.configuration.tags]
        capacity_provider.region = self.region
        capacity_provider.tags.append({
            "key": "Name",
            "value": capacity_provider.name
        })

        capacity_provider.auto_scaling_group_provider = {
            "autoScalingGroupArn": auto_scaling_group.arn,
            "managedScaling": {
                "status": "DISABLED",
                "targetCapacity": 70,
                "minimumScalingStepSize": 1,
                "maximumScalingStepSize": 10000,
                "instanceWarmupPeriod": 300
            },
            "managedTerminationProtection": "DISABLED"
        }

        self.aws_api.provision_ecs_capacity_provider(capacity_provider)

        return capacity_provider

    def attach_hagent_capacity_provider_to_ecs_cluster(self, ecs_cluster):
        """
        Attach provisioned instances to this cluster.

        :param ecs_cluster:
        :return:
        """

        default_capacity_provider_strategy = [
            {
                "capacityProvider": self.configuration.hagent_container_instance_capacity_provider_name,
                "weight": 1,
                "base": 0
            }
        ]
        self.aws_api.attach_capacity_providers_to_ecs_cluster(ecs_cluster, [
            self.configuration.hagent_container_instance_capacity_provider_name], default_capacity_provider_strategy)

        return True

    def update_hagent_auto_scaling_group_desired_count(self, auto_scaling_group):
        """
        EC2 instances auto scaling group for the ECS cluster.

        :param auto_scaling_group:
        :return:
        """

        auto_scaling_group.desired_capacity = self.configuration.container_instance_hagent_auto_scaling_group_desired_capacity
        self.aws_api.provision_auto_scaling_group(auto_scaling_group)

    def generate_hagent_user_data(self):
        """
        EC2 container instance user data to run on ec2 start.

        :return:
        """

        str_user_data = "#!/bin/bash\n" +\
        f'echo "ECS_CLUSTER={self.configuration.hagent_cluster_name}" >> /etc/ecs/ecs.config'

        user_data = self.aws_api.ec2_client.generate_user_data(str_user_data)
        return user_data

    def provision_container_instance_iam_profile(self):
        """
        Standard.

        :return:
        """

        assume_role_policy = """{
                "Version": "2012-10-17",
                "Statement": [
                {
                "Effect": "Allow",
                "Principal": {
                "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
                }
                ]
                }"""

        iam_role = IamRole({})
        iam_role.name = self.configuration.hagent_container_instance_role_name
        iam_role.assume_role_policy_document = assume_role_policy
        iam_role.description = self.configuration.hagent_container_instance_role_name
        iam_role.max_session_duration = 3600
        iam_role.tags = [{
            "Key": "Name",
            "Value": iam_role.name
        }]

        iam_role.path = self.configuration.iam_path
        iam_role.managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"]
        self.aws_api.iam_client.provision_role(iam_role)

        iam_instance_profile = IamInstanceProfile({})
        iam_instance_profile.name = self.configuration.hagent_container_instance_profile_name
        iam_instance_profile.path = self.configuration.iam_path
        iam_instance_profile.tags = [{
            "Key": "Name",
            "Value": iam_instance_profile.name
        }]
        iam_instance_profile.roles = [{"RoleName": iam_role.name}]
        self.aws_api.iam_client.provision_instance_profile(iam_instance_profile)
        return iam_instance_profile

