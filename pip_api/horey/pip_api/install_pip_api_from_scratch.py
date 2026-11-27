"""
Install the package and its dependencies from scratch.
Prerequisites: python, pip, OS (Mac, Linux or Windows)

"""
import os
import logging
import argparse

from static_methods import StaticMethods
from requirement import Requirement


def install_dependencies():
    """
    Install system dependencies.

    :return:
    """

    requirement = Requirement("", "wheel")
    StaticMethods.install_requirement_default(requirement)


def install_pip_api():
    """
    Install the pip api.

    :return:
    """

    install_dependencies()

    StaticMethods.install_requirements(StaticMethods.get_requirements_file_path(StaticMethods.HOREY_REPO_PATH, "pip_api"), {"horey": StaticMethods.HOREY_REPO_PATH})
    requirement_pip_api = Requirement("", "horey.pip_api")
    requirement_pip_api.multi_package_repo_path = StaticMethods.HOREY_REPO_PATH
    StaticMethods.install_multi_package_repo_requirement(requirement_pip_api)


def main():
    """
    Initialize the logger and run install routine.

    :return:
    """

    logger = logging.getLogger("main")
    logger.setLevel("INFO")

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "install_from_scratch.log"))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    StaticMethods.logger = logger
    install_pip_api()


if __name__ == "__main__":
    description = "Install package"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--pip_api_configuration", type=str)
    args = parser.parse_args()
    main()
