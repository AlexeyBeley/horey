"""
Monitored workflows table.
"""

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from horey.github_ui.db_models.base import Base


class MonitoredWorkflow(Base):
    """
    GitHub workflow of a repository that is monitored.
    """

    __tablename__ = "monitored_workflows"

    id: Mapped[int] = mapped_column(primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), nullable=False)
    workflow_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f"MonitoredWorkflow(id={self.id!r}, repository_id={self.repository_id!r}, workflow_name={self.workflow_name!r})"
