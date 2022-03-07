from horey.pip_api.pip_api import PipAPI
import os


def test_init():
    pip_api = PipAPI()
    assert isinstance(pip_api, PipAPI)


def test_init_packages():
    pip_api = PipAPI(venv_dir_path="/Users/alexey.beley/private/horey/serverless/tests/build/_venv")
    pip_api.init_packages()

    assert isinstance(pip_api.packages, list)


if __name__ == "__main__":
    #test_init()
    test_init_packages()
    #test_check_swap()
