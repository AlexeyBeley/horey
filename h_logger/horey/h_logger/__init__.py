"""
Logging package. Log formatting and routing.
"""

from .h_logger import get_logger
from .formatter import MultilineFormatter

__version__ = "1.0.0"

__all__ = ["get_logger", "MultilineFormatter"]
