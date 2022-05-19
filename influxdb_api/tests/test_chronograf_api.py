import pdb

import pytest
import os

from horey.chronograf_api.chronograf_api import ChronografAPI
from horey.chronograf_api.chronograf_api_configuration_policy import ChronografAPIConfigurationPolicy


configuration = ChronografAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "chronograf_api_configuration_values.py"))
configuration.init_from_file()

chronograf_api = ChronografAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_init_chronograf_api():
    chronograf_api_ = ChronografAPI(configuration=configuration)
    assert isinstance(chronograf_api_, ChronografAPI)


if __name__ == "__main__":
    #test_init_sources()
    #test_init_kapacitors()
    test_init_chronograf_api()
