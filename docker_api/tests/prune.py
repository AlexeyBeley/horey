"""
Prune docker containers
"""

from time import perf_counter
from datetime import datetime, timedelta
from horey.docker_api.docker_api import DockerAPI
from horey.h_logger import get_logger

logger = get_logger()

start = perf_counter()
date_now = datetime.now()
date_limit = date_now - timedelta(hours=1)
self = DockerAPI()
all_containers = self.client.containers.list(all=True)
logger.info(f"Fetched all containers in {perf_counter()-start}")

counter = 0

for container in all_containers:
    # '2024-08-01T17:38:24.420772541Z'
    if container.attrs["State"]["Status"].lower() == "running":
        # running container has finished date '0001-01-01T00:00:00'
        continue
    str_finished_date = container.attrs["State"]["FinishedAt"]
    str_finished_date = str_finished_date[:str_finished_date.rfind(".")]
    date_finished = datetime.strptime(str_finished_date, "%Y-%m-%dT%H:%M:%S")
    if date_limit > date_finished:
        logger.info(f"Removing {counter}/{len(all_containers)} container: {container.id}")
        counter += 1
        container.remove()

logger.info(f"Finished deleting {counter}/{len(all_containers)} containers after {perf_counter() - start}")
