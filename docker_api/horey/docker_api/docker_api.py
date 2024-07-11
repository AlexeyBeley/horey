"""
Docker API - used to communicate with docker service.

"""

import datetime
import getpass
import os.path
import platform
from time import perf_counter

import docker
from docker.errors import BuildError
from horey.h_logger import get_logger

logger = get_logger()


class DockerAPI:
    """
    Docker API main class

    """

    def __init__(self):
        if "macos" in platform.platform().lower():
            self.client = docker.DockerClient(base_url=f'unix:///Users/{getpass.getuser()}/.docker/run/docker.sock')
        else:
            self.client = docker.from_env(timeout=60*10)

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
        return ret

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
            build_start = perf_counter()
            docker_image, build_log = self.client.images.build(
                path=dockerfile_directory_path, tag=tag, nocache=nocache
            )
            build_end = perf_counter()
        except BuildError as exception_instance:
            self.print_log(exception_instance.build_log)
            raise

        logger.info(f"Finished building image in {build_end-build_start} seconds")
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
            return True

        key = "stream"
        if key in log_line:
            logger.info(log_line[key])
            return True

        key = "aux"
        if key in log_line:
            logger.info(log_line[key])
            return True

        key = "error"
        if key in log_line:
            logger.exception(log_line)
            raise DockerAPI.OutputError(log_line)

        logger.error(f"Unknown keys in: {log_line}")
        return True

    def tag_image(self, image, tags):
        """
        Tag image with new tags.

        @param image:
        @param tags:
        @return:
        """
        if not isinstance(tags, list):
            raise ValueError(f"Tags should be a list, received: {type(tags)}: {tags}")

        if len(tags) == 0:
            return True
        image.tag(tags[0])
        return self.tag_image(image, tags[1:])

    def upload_images(self, repo_tags):
        """
        Upload images based on the tags.

        @param repo_tags:
        @return:
        """

        errors_detected = False
        logger.info(f"Uploading image to repository {repo_tags}")
        for repository in repo_tags:
            logger.info(f"Uploading {repository} to repository")
            time_start = datetime.datetime.now()
            for log_line in self.client.images.push(
                repository=repository, stream=True, decode=True
            ):
                try:
                    self.print_log_line(log_line)
                except DockerAPI.OutputError:
                    errors_detected = True

            time_end = datetime.datetime.now()
            if errors_detected:
                raise RuntimeError(f"Failed to upload {repository} took {time_end-time_start} time.")

            logger.info(
                f"Uploading repository {repository} took {time_end-time_start} time."
            )
        return True

    def pull_images(self, repo, tag=None, all_tags=False):
        """
        Pull image or images.

        @param repo:
        @param tag:
        @param all_tags: NOT specific tags, ALL images being pulled. Very slow!
        @return:
        """

        logger.info(f"Pulling image from repository: {repo}, tag: {tag}")
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
    def kill_container(container, remove=False, wait_to_finish=None):
        """
        Kill the running container.

        @param container:
        @param remove:
        @param wait_to_finish:
        @return:
        """

        logger.info(f"Killing container: {container.id}.")
        try:
            container.wait(timeout=wait_to_finish)
        except Exception as inst_error:
            if "Read timed out" not in repr(inst_error):
                raise

        try:
            container.kill()
        except docker.errors.APIError as inst_error:
            if "is not running" not in str(inst_error):
                raise

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

    def remove_image(self, image_id, force=True, wait_to_finish=20*60, childless=False):
        """
        Remove image.

        @param image_id:
        @param force:
        @param wait_to_finish:
        @return:
        :param childless: Do not look for children - helpful when there are many images.
        """

        logger.info(f"Start removing image: {image_id}")

        lst_ret = []
        image_children = None
        if force:
            all_images = self.get_all_images()
            main_image = list(filter(lambda _img: _img.id == image_id, all_images))
            if len(main_image) != 1:
                raise ValueError(f"{image_id=}, {len(main_image)=}")
            main_image = main_image[0]

            if not childless:
                image_children = self.get_child_image_ids(image_id, all_images)
                for child_image_id in image_children:
                    lst_ret += self.remove_image(child_image_id, force=True)

            for container in self.get_containers_by_image(image_id):
                self.kill_container(container, remove=True, wait_to_finish=wait_to_finish)

            if image_children and not main_image.tags:
                logger.info(f"Untagged parent image automatically removed by docker after all children removed: {image_id}.")
                lst_ret.append(image_id)
                return lst_ret

        logger.info(f"Removing image: {image_id}.")

        self.client.images.remove(image_id, force=force)
        lst_ret.append(image_id)

        return lst_ret

    def get_all_images(self, repo_name=None):
        """
        List local images.
        Caution: If you need remote images in ECR use boto3.

        @param repo_name:
        @return:
        """

        return self.client.images.list(name=repo_name, all=True)

    def get_child_image_ids(self, image_id, all_images):
        """
        Return the children of the image.

        :return:
        """

        child_ids = []
        candidates = [image for image in all_images if image_id in image.id]
        if len(candidates) != 1:
            raise RuntimeError(f"Found {len(candidates)=} with {image_id=}")
        for image in all_images:
            if image.attrs["Parent"] == image_id:
                child_ids.append(image.id)

        logger.info(f"{image_id=} {child_ids=}")
        return child_ids

    def save(self, image, file_path):
        """
        Save image to file.

        Example:

            >>> image = cli.images.get("busybox:latest")
            >>> f = open('/tmp/busybox-latest.tar', 'wb')
            >>> for chunk in image.save():
            >>>   f.write(chunk)
            >>> f.close()
        :param file_path:
        :param image:
        :return:
        """

        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "wb") as file_handler:
            for chunk in image.save():
                file_handler.write(chunk)

        return os.path.exists(file_path)

    def load(self, file_path):
        """
        Load from file.

        :param file_path:
        :return:
        """

        with open(file_path, "rb") as file_handler:
            data = file_handler.read()

        images = self.client.images.load(data)

        if not isinstance(images, list):
            raise ValueError(f"Expected list: {images=}")

        if len(images) != 1:
            raise ValueError(f"Expected list of length 1: {images=}")

        return images[0]

    def get_all_ancestors(self, image_id, all_images=None):
        """
        Generate list of ancestors.

        :param image_id:
        :return:
        """

        if all_images is None:
            all_images = {image.id: image for image in self.get_all_images()}
            if not all_images[image_id].attrs["Parent"]:
                return []
            return self.get_all_ancestors(all_images[image_id].attrs["Parent"], all_images=all_images)

        if not all_images[image_id].attrs["Parent"]:
            return [image_id]

        return [image_id] + self.get_all_ancestors(all_images[image_id].attrs["Parent"], all_images=all_images)

    class OutputError(RuntimeError):
        """
        Error caught in a log line.
        """
