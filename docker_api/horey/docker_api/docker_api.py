import datetime

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

    def get_image(self, name):
        logger.info(f"Getting image: '{name}'")
        docker_image = self.client.images.get(name)
        return docker_image

    def build(self, dockerfile_directory_path, tags, nocache=True):
        logger.info(f"Starting building image {dockerfile_directory_path}, {tags}")
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
        key = "status"
        if key in log_line:
            return logger.info(log_line[key])
        
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

    def upload_image(self, repo_tags):
        logger.info(f"Uploading image to repository {repo_tags}")
        for repository in repo_tags:
            time_start = datetime.datetime.now()
            for log_line in self.client.images.push(repository=repository, stream=True, decode=True):
                self.print_log_line(log_line)
            time_end = datetime.datetime.now()
            logger.info(f"Uploading repository {repository} took {time_end-time_start} time.")

    def pull_image(self, repo, tag=None):
        logger.info(f"Pulling image from repository {repo}")
        if tag is not None and repo.find(":") > -1:
            raise RuntimeError(f"Using both repo tag and tag kwarg: {repo}, {tag}")
        images = self.client.images.pull(repository=repo, tag=tag, all_tags=True, decode=True)
        for image in images:
            logger.info(f"Image tags: {image.attrs['RepoTags']}")
            if repo in image.attrs["RepoTags"]:
                return image
        raise RuntimeError(f"Image not found: {repo}, tag = {tag}")

    def copy_image(self, src_repo_with_tag, dst_repo_name, copy_all_tags=True):
        image = self.pull_image(src_repo_with_tag)
        repo, tag = self.split_repo_with_tag(src_repo_with_tag)
        if copy_all_tags:
            logger.info(f"Preparing dst tags: {image.attrs['RepoTags']}")
            dst_tags = [f"{dst_repo_name}:{self.split_repo_with_tag(image_tag)[1]}"
                        for image_tag in image.attrs["RepoTags"] if image_tag.startswith(repo)]
        else:
            dst_tags = [f"{dst_repo_name}:{tag}"]

        self.tag_image(image, dst_tags)
        self.upload_image(dst_tags)

    @staticmethod
    def split_repo_with_tag(repo_with_tag):
        if ":" not in repo_with_tag:
            raise ValueError(f"Untagged repo: {repo_with_tag}")

        if repo_with_tag.count(":") > 1:
            raise ValueError(f"Expected single ':' in repo repo: {repo_with_tag}")

        repo, tag = repo_with_tag.split(":")
        return repo, tag

    @staticmethod
    def kill_container(container, remove=False):
        container.kill()
        if remove:
            container.remove()

    def get_containers_by_image(self, image_id):
        ret = [container for container in self.client.containers.list() if image_id == container.image.id]
        return ret

    def remove_image(self, image_id, force=True):
        try:
            self.client.images.remove(image_id, force=force)
        except Exception as exception_instance:
            logger.info(f"Exception received: {repr(exception_instance)}. Endof exception.")
            if "image is being used by running container" not in repr(exception_instance):
                raise

            for container in self.get_containers_by_image(image_id):
                self.kill_container(container, remove=True)

            self.client.images.remove(image_id, force=force)

