"""
Testing docker_api module.

"""


import pytest
from horey.docker_api.docker_actor import prune_old_images, pull, login


@pytest.mark.unit
def test_prune_old_images():
    """
    Test basic init.

    @return:
    """

    class arguments:
       limit = 4

    assert prune_old_images(arguments)


@pytest.mark.unit
def test_pull():
    """
    Test basic init.

    @return:
    """

    class arguments:
       image = "public.ecr.aws/lambda/python:3.12"

    assert pull(arguments)

@pytest.mark.unit
def test_login():
    """
    Test basic init.

    @return:
    """

    class arguments:
        host = ""
        username = ""
        password = ""

    assert login(arguments)