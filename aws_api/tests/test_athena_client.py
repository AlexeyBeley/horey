"""
Test athena client

"""


from horey.aws_api.aws_clients.athena_client import AthenaClient

# pylint: disable= missing-function-docstring

def test_init_athena_client():
    assert isinstance(AthenaClient(), AthenaClient)


def test_get():
    AthenaClient().get_all_template_entities()
    assert isinstance(AthenaClient(), AthenaClient)
