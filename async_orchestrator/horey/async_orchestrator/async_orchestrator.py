"""
Async orchestrator

"""

import datetime
import sys
import time
import threading
from horey.h_logger import get_logger

logger = get_logger()


class AsyncOrchestrator:
    """
    Main class.

    """

    def __init__(self):
        self.tasks = {}

    def start_task(self, task):
        """
        Start single task.

        :param task:
        :return:
        """

        logger.info(f"Starting task '{task.id}' at {time.strftime('%X')}")
        if task.id in self.tasks:
            raise RuntimeError(f"Task with id {task.id} already in tasks: {self.tasks}")
        self.tasks[task.id] = task

        thread = threading.Thread(target=self.task_runner_thread, args=(task,))
        thread.start()
        logger.info(f"Started thread for '{task.id}' in start_task at {time.strftime('%X')}")

    @staticmethod
    def task_runner_thread(task):
        """
        Task running thread

        :param task:
        :return:
        """
        logger.info(f"started task_runner_thread at {time.strftime('%X')}")

        try:
            task.started = True
            logger.info(f"Setting task {task.id} as started")
            task.exit_code = 1
            logger.info(f"Task '{task.id}' Set exit code = {task.exit_code}")
            task.result = task.function()
            task.exit_code = 0
            logger.info(f"Task '{task.id}' Set exit code = {task.exit_code}")
        except Exception as error_inst:
            task.exception = error_inst
            logger.error(f"Exception output start {task.id}")
            logger.exception(error_inst)
        finally:
            logger.info(f"Setting task {task.id} as finished")
            task.finished = True

        logger.info(f"finished task_runner_thread at {time.strftime('%X')}")

    def wait_for_tasks(self, sleep_time=1):
        """
        Wait for all tasks to finish.

        :return:
        """
        logger.info(f"started wait_for_tasks at {time.strftime('%X')}")

        end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        while datetime.datetime.now() < end_time:
            for task in self.tasks.values():
                if not task.finished:
                    logger.info(f"Task {task.id} is not yet finished")
                    break
            else:
                logger.info("All tasks have finished.")
                return True

            logger.info(f"Waiting for tasks to finish. Going to sleep {sleep_time}")
            time.sleep(sleep_time)
        raise TimeoutError(f"Finished wait_for_tasks at {time.strftime('%X')}")

    # pylint: disable= too-many-arguments
    def get_task_result(self, task_id, sleep_time=1, timeout=20*60, start_timeout=60, silent_exit=False):
        """
        Wait for all tasks to finish.

        :return:
        """
        logger.info(f"started wait_for_tasks at {time.strftime('%X')}")
        now = datetime.datetime.now()
        end_time = now + datetime.timedelta(seconds=timeout)
        end_time_for_task_to_start = now + datetime.timedelta(seconds=start_timeout)

        while datetime.datetime.now() < end_time_for_task_to_start:
            if self.tasks.get(task_id):
                break
            logger.info(f"Waiting for task '{task_id}' to start. Going to sleep {sleep_time}")
            time.sleep(sleep_time)
        else:
            raise TimeoutError(f"Task '{task_id}' did not start for {start_timeout} seconds. {time.strftime('%X')}")

        task = self.tasks.get(task_id)

        while datetime.datetime.now() < end_time:
            if task.finished:
                if task.exception:
                    raise RuntimeError(f"Task failed: '{task_id}' look for 'Exception output start {task_id}' ") from task.exception
                if task.exit_code != 0:
                    logger.info(f"Task '{task_id}' exit code = {task.exit_code}")
                    if task.exit_code is None:
                        raise RuntimeError(f"Task exit code was not set: '{task_id}' exit code is None")

                    if task.exit_code == 1:
                        time.sleep(1)

                    if task.exit_code == 0:
                        continue

                    if silent_exit:
                        sys.exit(task.exit_code)
                    raise RuntimeError(f"Task failed: '{task_id}' with exit code != 0")
                return task.result

            logger.info(f"Waiting for task '{task_id}' to start and finish. Going to sleep {sleep_time}")
            time.sleep(sleep_time)
        raise TimeoutError(f"Task did not finish during {timeout} seconds. {time.strftime('%X')}")

    class Task:
        """
        Task to be run
        """
        def __init__(self, task_id, function):
            self.id = task_id
            self.function = function
            self.started = True
            self.result = None
            self.finished = False
            self.exception = None
            self.exit_code = None
