"""
Test async orchestrator
"""

import time
import pytest

from horey.async_orchestrator.async_orchestrator import AsyncOrchestrator

# pylint: disable = missing-function-docstring
def test(timeout=1):
    print("Started test function")
    time.sleep(timeout)
    print("Started test function")
    return 1


@pytest.mark.wip
def test_start_task():
    async_orchestrator = AsyncOrchestrator()


    task = AsyncOrchestrator.Task("test", test)
    async_orchestrator.start_task(task)
    async_orchestrator.wait_for_tasks()
    assert task.result == test(timeout=0)

@pytest.mark.wip
def test_get_task_result():
    async_orchestrator = AsyncOrchestrator()
    task = AsyncOrchestrator.Task("test", test)
    async_orchestrator.start_task(task)
    ret = async_orchestrator.get_task_result(task.id)
    assert ret == test(timeout=0)
