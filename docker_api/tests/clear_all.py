"""
Delete all images.

"""

from horey.docker_api.docker_api import DockerAPI
import os

import getpass
USERNAME = getpass.getuser()
#os.environ["DOCKER_HOST"] = f"unix:///Users/{USERNAME}/.docker/run/docker.sock"

docker_api = DockerAPI()


def get_childless_images(all_images):
    parent_ids = [image.attrs["Parent"] for image in all_images if image.attrs["Parent"]]
    return [image for image in all_images if image.attrs["Id"] not in parent_ids]


def main():
    all_images = docker_api.get_all_images()
    while all_images:
        print(f"All images: {len(all_images)}")

        childless_images = get_childless_images(all_images)
        print(f"Childless images: {len(childless_images)}")
        for image in childless_images:
            docker_api.remove_image(image.attrs["Id"], force=False)

        all_images = docker_api.get_all_images()


if __name__ == "__main__":
    main()
