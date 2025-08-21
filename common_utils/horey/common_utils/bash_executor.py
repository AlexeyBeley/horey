"""
Securely executes bash code
"""
import os
import json
import subprocess
import logging
import uuid
from time import perf_counter


def get_logger():
    """
    Generate local logger.

    :return:
    """

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s"
    )
    handler.setFormatter(formatter)
    _logger = logging.getLogger("bash_executor")
    _logger.setLevel("INFO")
    _logger.addHandler(handler)
    return _logger


class BashExecutor:
    """
    Main class.
    """
    _logger = None

    @staticmethod
    def set_logger(logger, override=False):
        """
        Set static logger.

        :param override:
        :param logger:
        :return:
        """

        if BashExecutor._logger is not None and not override:
            return True

        BashExecutor._logger = logger
        return True

    @staticmethod
    def run_bash(command, ignore_on_error_callback=None, timeout=60 * 10, debug=True, logger=None):
        """
        Run bash command, return stdout, stderr and return code.
        Timeout is used fot stuck commands - for example if the command expects for user input.
        Like dpkg installation approve - happens all the time with logstash package.

        @param timeout: In seconds. Default 10 minutes
        @param debug: print return code, stdout and stderr
        @param command:
        @param ignore_on_error_callback:
        @param logger:
        @return:
        """

        if not logger:
            logger = BashExecutor._logger or get_logger()

        logger.info(f"### Command Start ###")
        logger.info(f"run_bash: {command}")
        perf_counter_start = perf_counter()

        file_name = f"tmp-{str(uuid.uuid4())}.sh"
        with open(file_name, "w", encoding="utf-8") as file_handler:
            file_handler.write(command)
            command = f"/bin/bash {file_name}"

        try:
            ret = subprocess.run(
                [command], capture_output=True, shell=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as error:
            return_dict = {
                "stdout": "",
                "stderr": "TimeoutExpired: " + repr(error),
                "code": 1,
            }
            raise BashExecutor.BashError(json.dumps(return_dict))

        os.remove(file_name)
        return_dict = {
            "stdout": ret.stdout.decode().strip("\n"),
            "stderr": ret.stderr.decode().strip("\n"),
            "code": ret.returncode,
        }
        if debug:
            logger.info(f"return_code:{return_dict['code']}")

            stdout_log = "stdout:\n" + str(return_dict["stdout"])

            if stdout_log:
                stdout_log = stdout_log.strip("\n")

            for line in stdout_log.split("\n"):
                logger.info(line)

            error_str = str(return_dict["stderr"])
            if error_str:
                error_str = error_str.strip("\n")
                stderr_log = "stderr:\n" + error_str
                for line in stderr_log.split("\n"):
                    logger.info(line)

        logger.info(f"### Command End {perf_counter() - perf_counter_start}###")
        if ret.returncode != 0:
            if ignore_on_error_callback is None:
                raise BashExecutor.BashError(json.dumps(return_dict))

            if not ignore_on_error_callback(return_dict):
                raise BashExecutor.BashError(json.dumps(return_dict))

        return return_dict

    class BashError(RuntimeError):
        """
        Error received in bash.
        """
