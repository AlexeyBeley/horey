"""
Async orchestrator

"""

import datetime
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

        logger.info(f"started start_task at {time.strftime('%X')}")
        if task.id in self.tasks:
            raise RuntimeError(f"Task with id {task.id} already in tasks: {self.tasks}")
        self.tasks[task.id] = task

        thread = threading.Thread(target=self.task_runner_thread, args=(task,))
        thread.start()
        logger.info(f"finished start_task at {time.strftime('%X')}")

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
            task.result = task.function()
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

    def get_task_result(self, task_id, sleep_time=1, timeout=20*60):
        """
        Wait for all tasks to finish.

        :return:
        """
        logger.info(f"started wait_for_tasks at {time.strftime('%X')}")

        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() < end_time:
            task = self.tasks.get(task_id)
            if task and task.finished:
                return task.result

            logger.info(f"Waiting for task to start and finish. Going to sleep {sleep_time}")
            time.sleep(sleep_time)
        raise TimeoutError(f"Finished get_task_result at {time.strftime('%X')}")

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
