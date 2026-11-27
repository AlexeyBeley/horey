"""
Declarative base for all the models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Common base. Collects the metadata of all the models.
    """
