"""
Repositories table.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from horey.github_ui.db_models.base import Base


class Repository(Base):
    """
    GitHub repository.
    """

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    last_update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"Repository(id={self.id!r}, owner={self.owner!r}, name={self.name!r})"
