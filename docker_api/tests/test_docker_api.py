from horey.docker_api.docker_api import DockerAPI
import os


def test_init_docker_api():
    assert isinstance(DockerAPI(), DockerAPI)


def test_build():
    docker_api = DockerAPI()
    image = docker_api.build(os.path.dirname(os.path.abspath(__file__)), ["horey-test:latest"])
    assert image is not None


def test_get_image():
    docker_api = DockerAPI()
    image = docker_api.get_image("horey-test:latest")
    assert image is not None


if __name__ == "__main__":
    test_init_docker_api()
    test_build()
    test_get_image()
