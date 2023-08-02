"""
Docker API - used to communicate with docker service.

"""

import datetime

import docker
from docker.errors import BuildError
from horey.h_logger import get_logger

logger = get_logger()


class DockerAPI:
    """
    Docker API main class

    """

    def __init__(self):
        self.client = docker.from_env()

    def login(self, registry, username, password):
        """
        Authenticate with a registry. Similar to the ``docker login`` command.

        @param registry:
        @param username:
        @param password:
        @return:
        """

        ret = self.client.login(registry=registry, username=username, password=password)
        logger.info(ret)

    def get_image(self, name):
        """
        Get local image.

        @param name:
        @return:
        """

        logger.info(f"Getting image: '{name}'")
        docker_image = self.client.images.get(name)
        return docker_image

    def build(self, dockerfile_directory_path, tags, nocache=True):
        """
        Build image.

        @param dockerfile_directory_path:
        @param tags:
        @param nocache:
        @return:
        """

        logger.info(f"Starting building image {dockerfile_directory_path}, {tags}")
        if not isinstance(tags, list):
            raise ValueError(
                f"'tags' must be of a type 'list' received {tags}: type: {type(tags)}"
            )

        tag = tags[0] if len(tags) > 0 else "latest"
        try:
            docker_image, build_log = self.client.images.build(
                path=dockerfile_directory_path, tag=tag, nocache=nocache
            )
        except BuildError as exception_instance:
            self.print_log(exception_instance.build_log)
            raise

        logger.info("Finished building image")
        self.print_log(build_log)
        self.tag_image(docker_image, tags[1:])
        return docker_image

    def print_log(self, log_iterator):
        """
        Print log from iterable.

        @param log_iterator:
        @return:
        """

        for log_line in log_iterator:
            self.print_log_line(log_line)

    @staticmethod
    def print_log_line(log_line):
        """
        Pretty print of a log line.

        @param log_line:
        @return:
        """

        key = "status"
        if key in log_line:
            logger.info(log_line[key])
            return

        key = "stream"
        if key in log_line:
            logger.info(log_line[key])
            return

        key = "aux"
        if key in log_line:
            logger.info(log_line[key])
            return

        key = "error"
        if key in log_line:
            logger.error(log_line[key])
            return

        logger.error(f"Unknown keys in: {log_line}")

    def tag_image(self, image, tags):
        """
        Tag image with new tags.

        @param image:
        @param tags:
        @return:
        """

        if len(tags) == 0:
            return
        image.tag(tags[0])
        self.tag_image(image, tags[1:])

    def upload_images(self, repo_tags):
        """
        Upload images based on the tags.

        @param repo_tags:
        @return:
        """

        logger.info(f"Uploading image to repository {repo_tags}")
        for repository in repo_tags:
            logger.info(f"Uploading {repository} to repository")
            time_start = datetime.datetime.now()
            for log_line in self.client.images.push(
                repository=repository, stream=True, decode=True
            ):
                self.print_log_line(log_line)
            time_end = datetime.datetime.now()
            logger.info(
                f"Uploading repository {repository} took {time_end-time_start} time."
            )

    def pull_images(self, repo, tag=None, all_tags=False):
        """
        Pull image or images.

        @param repo:
        @param tag:
        @param all_tags: NOT specific tags, ALL images being pulled. Very slow!
        @return:
        """

        logger.info(f"Pulling image from repository {repo}")
        if tag is not None and repo.find(":") > -1:
            raise RuntimeError(f"Using both repo tag and tag kwarg: {repo}, {tag}")
        images = self.client.images.pull(
            repository=repo, tag=tag, all_tags=all_tags, decode=True
        )
        if not isinstance(images, list):
            images = [images]

        return images

    def copy_image(self, src_repo_with_tag, dst_repo_name, copy_all_tags=True):
        """
        Copy image from one repo to the other.

        @param src_repo_with_tag:
        @param dst_repo_name:
        @param copy_all_tags:
        @return:
        """

        images = self.pull_images(src_repo_with_tag, all_tags=copy_all_tags)
        if len(images) < 1:
            raise RuntimeError(
                f"Expected > 1 docker image with tag: {src_repo_with_tag}"
            )

        image = images[0]
        repo, tag = self.split_repo_with_tag(src_repo_with_tag)
        if copy_all_tags:
            logger.info(f"Preparing dst tags: {image.attrs['RepoTags']}")
            dst_tags = [
                f"{dst_repo_name}:{self.split_repo_with_tag(image_tag)[1]}"
                for image_tag in image.attrs["RepoTags"]
                if image_tag.startswith(repo)
            ]
        else:
            dst_tags = [f"{dst_repo_name}:{tag}"]

        self.tag_image(image, dst_tags)
        self.upload_images(dst_tags)

    @staticmethod
    def split_repo_with_tag(repo_with_tag):
        """
        Split repo with tag to repo and tag.

        @param repo_with_tag:
        @return:
        """
        if ":" not in repo_with_tag:
            raise ValueError(f"Untagged repo: {repo_with_tag}")

        if repo_with_tag.count(":") > 1:
            raise ValueError(f"Expected single ':' in repo repo: {repo_with_tag}")

        repo, tag = repo_with_tag.split(":")
        return repo, tag

    @staticmethod
    def kill_container(container, remove=False):
        """
        Kill the running container.

        @param container:
        @param remove:
        @return:
        """

        logger.info(f"Killing container: {container.id}.")
        container.kill()
        if remove:
            logger.info(f"Removing container: {container.id}.")
            container.remove()

    def get_containers_by_image(self, image_id, all_containers=False):
        """
        Get all containers.

        @param all_containers:
        @param image_id:
        @return:
        """

        ret = [
            container
            for container in self.client.containers.list(all=all_containers)
            if image_id == container.image.id
        ]
        return ret

    def remove_image(self, image_id, force=True):
        """
        Remove image.

        @param image_id:
        @param force:
        @return:
        """

        logger.info(f"Removing image: {image_id}.")
        if force:
            for child_image_id in self.get_child_image_ids(image_id):
                self.remove_image(child_image_id, force=True)

            for container in self.get_containers_by_image(image_id):
                self.kill_container(container, remove=True)

        self.client.images.remove(image_id, force=force)

    def get_all_images(self, repo_name=None):
        """
        List local images.
        Caution: If you need remote images in ECR use boto3.

        @param repo_name:
        @return:
        """

        return self.client.images.list(name=repo_name, all=True)

    def get_child_image_ids(self, image_id):
        """
        Return the children of the image.

        :return:
        """
        breakpoint()