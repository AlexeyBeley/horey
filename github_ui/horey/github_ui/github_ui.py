"""
GitHub UI logic.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from horey.github_api.github_api import GithubAPI
from horey.github_api.github_api_configuration_policy import GithubAPIConfigurationPolicy
from horey.github_ui.db_models import MonitoredWorkflow, Repository
from horey.github_ui.github_ui_configuration_policy import GithubUIConfigurationPolicy
from horey.h_logger import get_logger
from horey.postgres_api.postgres_api import PostgresAPI
from horey.postgres_api.postgres_api_configuration_policy import PostgresAPIConfigurationPolicy

logger = get_logger()


class GithubUI:
    """
    Main class.

    """

    def __init__(self, configuration: GithubUIConfigurationPolicy = None):
        self.configuration = configuration
        self._github_api = None
        self._postgres_api = None

    @property
    def github_api(self) -> GithubAPI:
        """
        Lazy GithubAPI, configured from the configuration's github_api_configuration_file_path.

        :return:
        """

        if self._github_api is None:
            file_path = self.configuration.github_api_configuration_file_path if self.configuration else None
            if file_path is None:
                raise ValueError("github_api_configuration_file_path was not set")

            github_api_configuration = GithubAPIConfigurationPolicy()
            github_api_configuration.configuration_file_full_path = file_path
            github_api_configuration.init_from_file()
            self._github_api = GithubAPI(configuration=github_api_configuration)
        return self._github_api

    @github_api.setter
    def github_api(self, value):
        self._github_api = value

    @property
    def postgres_api(self) -> PostgresAPI:
        """
        Lazy PostgresAPI, configured from the configuration's postgres_api_configuration_file_path.
        The connection itself is opened on first use.

        :return:
        """

        if self._postgres_api is None:
            file_path = self.configuration.postgres_api_configuration_file_path if self.configuration else None
            if file_path is None:
                raise ValueError("postgres_api_configuration_file_path was not set")

            postgres_api_configuration = PostgresAPIConfigurationPolicy()
            postgres_api_configuration.configuration_file_full_path = file_path
            postgres_api_configuration.init_from_file()
            self._postgres_api = PostgresAPI(configuration=postgres_api_configuration)
        return self._postgres_api

    @postgres_api.setter
    def postgres_api(self, value):
        self._postgres_api = value

    def fetch_repositories(self):
        """
        Names of all the repositories under the configured owner (organization).
        The repositories are saved to the repositories table.

        :return:
        """

        repositories = self.github_api.init_repositories()
        names = [repository["name"] for repository in repositories]
        self.save_repositories(names)
        return names

    def save_repositories(self, names: list[str]):
        """
        Add the repositories of the configured owner that are not yet in the repositories table.
        last_update_time of all the given repositories is set to now.

        :param names: Repository names.
        :return:
        """

        owner = self.github_api.configuration.owner
        now = datetime.now(timezone.utc)
        with Session(self.postgres_api.engine) as session:
            existing = {repository.name: repository for repository in
                        session.scalars(select(Repository).where(Repository.owner == owner))}
            for name in names:
                if name in existing:
                    existing[name].last_update_time = now
                else:
                    session.add(Repository(name=name, owner=owner, last_update_time=now))
            session.commit()

    def add_monitored_workflows(self, workflows_by_repository: dict[str, list[str]]):
        """
        Add the workflows to the monitored_workflows table, if they are not there yet.
        A repository that is not yet in the repositories table is added.

        :param workflows_by_repository: Repository name -> names of its workflows.
        :return:
        """

        owner = self.github_api.configuration.owner
        with Session(self.postgres_api.engine) as session:
            for repository_name, workflow_names in workflows_by_repository.items():
                repository = session.scalars(select(Repository).where(
                    Repository.owner == owner, Repository.name == repository_name)).first()
                if repository is None:
                    repository = Repository(name=repository_name, owner=owner, last_update_time=datetime.now(timezone.utc))
                    session.add(repository)
                    session.flush()

                monitored = set(session.scalars(select(MonitoredWorkflow.workflow_name).where(
                    MonitoredWorkflow.repository_id == repository.id)))
                for workflow_name in workflow_names:
                    if workflow_name not in monitored:
                        session.add(MonitoredWorkflow(repository_id=repository.id, workflow_name=workflow_name))
                        monitored.add(workflow_name)
            session.commit()

    def fetch_workflows(self, repository: str):
        """
        Names of the workflows of the repository.

        :param repository: Repository name.
        :return:
        """

        return [workflow.name for workflow in self.github_api.get_repository_workflows(repository)]

    def get_monitored_workflows_status(self):
        """
        Monitored workflows with their current status (status column of monitored_workflows, None if not yet known).

        :return: [{"repository": ..., "workflow": ..., "status": ...}]
        """

        owner = self.github_api.configuration.owner
        statement = (select(Repository.name, MonitoredWorkflow.workflow_name, MonitoredWorkflow.status)
                     .join(Repository, Repository.id == MonitoredWorkflow.repository_id)
                     .where(Repository.owner == owner)
                     .order_by(Repository.name, MonitoredWorkflow.workflow_name))
        with Session(self.postgres_api.engine) as session:
            return [{"repository": repository, "workflow": workflow, "status": status}
                    for repository, workflow, status in session.execute(statement)]
