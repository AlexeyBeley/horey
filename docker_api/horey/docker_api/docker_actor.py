"""
Docker api entry point script.

"""

import argparse
import logging
import docker

logger = logging.Logger(__name__)

from horey.common_utils.actions_manager import ActionsManager
from horey.docker_api.docker_api import DockerAPI

docker_client = docker.from_env()
action_manager = ActionsManager()

# pylint: disable= missing-function-docstring


# region create_repository
def build_parser():
    description = "Build docker image"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--tag", required=True, type=str, help="Name repository to create"
    )
    return parser


def build(arguments) -> None:
    docker_client.images.build(path=".", tag=arguments.tag)


action_manager.register_action("build", build_parser, build)
# endregion


# region login
def login_parser():
    description = "Login to images' repo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--host", required=True, type=str, help="Hostname to login to")
    parser.add_argument("--username", required=True, type=str, help="User name")
    parser.add_argument("--password", required=True, type=str, help="Password")
    return parser


def login(arguments) -> None:
    ret = docker_client.login(
        registry=arguments.host,
        username=arguments.username,
        password=arguments.password,
    )
    logger.info(ret)


action_manager.register_action("login", login_parser, login)
# endregion

# region push
def push_parser():
    description = "Push image to repo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repository", required=True, type=str, help="Repo to push")
    parser.add_argument("--tag", required=True, type=str, help="Tag to push")
    parser.add_argument("--host", required=True, type=str, help="Hostname to login to")
    parser.add_argument("--username", required=True, type=str, help="User name")
    parser.add_argument("--password", required=True, type=str, help="Password")
    return parser


def push(arguments) -> None:
    auth_config = {
        "host": arguments.host,
        "username": arguments.username,
        "password": arguments.password,
    }
    for line in docker_client.images.push(
        repository=arguments.repository,
        tag=arguments.tag,
        auth_config=auth_config,
        stream=True,
        decode=True,
    ):
        print(line)


action_manager.register_action("push", push_parser, push)
# endregion


# region prune_old_images
def prune_old_images_parser():
    description = "delete images"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--limit", required=True, type=int, help="limit")
    parser.add_argument("--timeout", required=False, type=int, help="timeout for containers to gracefully stop")
    return parser


def prune_old_images(arguments) -> None:
    return DockerAPI().prune_old_images(arguments.limit)


action_manager.register_action("prune_old_images", prune_old_images_parser, prune_old_images)
# endregion

# region prune_old_images
def pull_parser():
    description = "Pull images"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--image", required=True, type=str, help="Image tag")
    return parser


def pull(arguments) -> None:
    return DockerAPI().pull_images(arguments.image)


action_manager.register_action("pull", pull_parser, pull)
# endregion

if __name__ == "__main__":
    action_manager.call_action()
