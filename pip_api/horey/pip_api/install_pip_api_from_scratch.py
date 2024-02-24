"""
Install the package and its dependencies from scratch.
Prerequisites: python, pip, OS (Mac, Linux or Windows)

"""
import os
import logging
from time import perf_counter

from subprocess import Popen, PIPE, STDOUT
from static_methods import StaticMethods


def execute(lst_command):
    """
    Run a command in a process.

    :param lst_command:
    :return:
    """

    start_time = perf_counter()
    StaticMethods.logger.info(f"Creating sub process: {start_time}")
    # pylint: disable= consider-using-with
    process = Popen(lst_command, stdout=PIPE, stderr=STDOUT)
    StaticMethods.logger.info(f"Started sub process: {perf_counter() - start_time}")

    try:
        if process.stderr is not None:
            StaticMethods.logger.error(process.stderr.read())

        if process.stdout is not None:
            StaticMethods.logger.info(process.stdout.read())
    except Exception:
        StaticMethods.logger.exception("Failed to read Popen stdout/stderr")


def install_pip_api():
    """
    Install the pip api.

    :return:
    """
    StaticMethods.install_requirements(StaticMethods.get_requirements_file_path(StaticMethods.HOREY_REPO_PATH, "pip_api"), {"horey": StaticMethods.HOREY_REPO_PATH})


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
    main()
