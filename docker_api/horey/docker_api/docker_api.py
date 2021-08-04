import sys
import pdb
import argparse
import json
import docker
from horey.h_logger import get_logger

logger = get_logger()


class DockerAPI:
    def __init__(self):
        self.client = docker.from_env()

    def login(self, registry, username, password):
        ret = self.client.login(registry=registry, username=username, password=password)
        logger.info(ret)

    def build(self, dockerfile_directory_path):
        self.client.images.build(path=dockerfile_directory_path)

    def push(self, arguments) -> None:
        auth_config = {"host": arguments.host, "username": arguments.username, "password": arguments.password}
        for line in docker_client.images.push(repository=arguments.repository, tag=arguments.tag, auth_config=auth_config, stream=True, decode=True):
            print(line)
