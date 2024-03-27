from horey.docker_api.docker_api import DockerAPI


docker_api = DockerAPI()

all_images = docker_api.get_all_images()
for image in all_images: docker_api.remove_image(image, force=True)
