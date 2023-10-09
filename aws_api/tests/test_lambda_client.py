"""
AWS lambda client

"""
import os

import pytest
from horey.aws_api.aws_clients.lambda_client import LambdaClient
from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.base_entities.region import Region


LambdaClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.wip
def test_init_lambda_client():
    assert isinstance(LambdaClient(), LambdaClient)

@pytest.mark.wip
def test_get_region_lambdas():
    lambda_client = LambdaClient()
    lambdas = lambda_client.get_region_lambdas(Region.get_region("us-west-2"))
    assert isinstance(lambdas, list)


@pytest.mark.wip
def test_yield_lambdas():
    client = LambdaClient()
    obj = None
    for obj in client.yield_lambdas(region=Region.get_region("us-west-2")):
        break
    assert obj.arn is not None

@pytest.mark.wip
def test_get_all_lambdas_full_information_false():
    client = LambdaClient()
    file_path = client.generate_cache_file_path(AWSLambda, "us-west-2", full_information=False, get_tags=False)
    assert client.get_all_lambdas(full_information=False)
    assert os.path.exists(file_path)


@pytest.mark.wip
def test_get_region_lambdas_region_full_information_true():
    client = LambdaClient()
    file_path = client.generate_cache_file_path(AWSLambda, "us-west-2", full_information=True, get_tags=False)
    assert client.get_region_lambdas(Region.get_region("us-west-2"), full_information=True)
    assert os.path.exists(file_path)

@pytest.mark.wip
def test_get_region_lambdas_region_full_information_false():
    client = LambdaClient()
    file_path = client.generate_cache_file_path(AWSLambda, "us-west-2", full_information=False, get_tags=False)
    assert client.get_region_lambdas(Region.get_region("us-west-2"), full_information=False)
    assert os.path.exists(file_path)
