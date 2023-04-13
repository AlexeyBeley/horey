"""
AWS lambda client

"""

from horey.aws_api.aws_clients.lambda_client import LambdaClient
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region

AWSAccount.set_aws_region(Region.get_region("us-west-2"))

# pylint: disable = missing-function-docstring


def test_init_lambda_client():
    assert isinstance(LambdaClient(), LambdaClient)


def test_get_region_lambdas():
    lambda_client = LambdaClient()
    lambdas = lambda_client.get_region_lambdas(Region.get_region("us-west-2"))
    assert isinstance(lambdas, list)


if __name__ == "__main__":
    test_init_lambda_client()
    test_get_region_lambdas()
