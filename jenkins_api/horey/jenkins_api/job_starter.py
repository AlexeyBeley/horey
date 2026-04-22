from horey.jenkins_api.jenkins_api import JenkinsAPI, JenkinsAPIConfigurationPolicy

configuration = JenkinsAPIConfigurationPolicy()
configuration.host = "HOST_PLACE_HOLDER"
configuration.username = "USERNAME_PLACE_HOLDER"
configuration.token = "TOKEN_PLACE_HOLDER"

manager = JenkinsAPI(configuration)
with open(arguments.build_info_file, encoding="utf-8") as file_handler:
    build_info = json.load(file_handler)
job = JenkinsJob(build_info["job_name"], build_info.get("parameters"))
manager.execute_jobs([job])
