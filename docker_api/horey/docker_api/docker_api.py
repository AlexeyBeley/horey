import sys
import pdb
import argparse
import json
import docker
from docker.errors import BuildError
from horey.h_logger import get_logger

logger = get_logger()


class DockerAPI:
    def __init__(self):
        self.client = docker.from_env()

    def login(self, registry, username, password):
        ret = self.client.login(registry=registry, username=username, password=password)
        logger.info(ret)

    def build(self, dockerfile_directory_path, tags, nocache=True):
        logger.info("Starting building image")
        if not isinstance(tags, list):
            raise ValueError(f"'tags' must be of a type 'list' received {tags}: type: {type(tags)}")

        tag = tags[0] if len(tags) > 0 else "latest"
        try:
            docker_image, build_log = self.client.images.build(path=dockerfile_directory_path, tag=tag, nocache=nocache)
        except BuildError as exception_instance:
            self.print_log(exception_instance.build_log)
            raise

        logger.info("Finished building image")

        self.print_log(build_log)
        self.tag_image(docker_image, tags[1:])
        return docker_image

    def print_log(self, log_iterator):
        for log_line in log_iterator:
            self.print_log_line(log_line)

    @staticmethod
    def print_log_line(log_line):
        key = "stream"
        if key in log_line:
            return logger.info(log_line[key])

        key = "aux"
        if key in log_line:
            return logger.info(log_line[key])

        key = "error"
        if key in log_line:
            return logger.error(log_line[key])

        logger.error(f"Unknown keys in: {log_line}")

    def tag_image(self, image, tags):
        if len(tags) == 0:
            return
        image.tag(tags[0])
        self.tag_image(image, tags[1:])

    def push_old(self, arguments) -> None:
        auth_config = {"host": arguments.host, "username": arguments.username, "password": arguments.password}
        for log_line in self.client.images.push(repository=arguments.repository, tag=arguments.tag, auth_config=auth_config, stream=True, decode=True):
            self.print_log_line(log_line)

    def upload_image(self, docker_image):
        repo_tags = [repo_tag for repo_tag in docker_image.attrs["RepoTags"]]
        for repository in repo_tags:
            pdb.set_trace()
            for log_line in self.client.images.push(repository=repository, stream=True, decode=True):
                self.print_log_line(log_line)
            pdb.set_trace()
