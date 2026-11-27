"""
Testing docker_api module.

"""


import pytest
from horey.infrastructure_api.infrastructure_api_actor import ecr_login


@pytest.mark.unit
def test_ecr_login():
    """
    Test basic init.

    @return:
    """

    class arguments:
       region = "us-west-2"

    assert ecr_login(arguments)



@pytest.mark.unit
def test_ecr_login_logout_false():
    """
    Test basic init.

    @return:
    """

    class arguments:
       region = "us-west-2"
       logout = "false"

    assert ecr_login(arguments)