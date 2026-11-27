"""
Pip api configuration
"""
import os

tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

venv_dir_path = os.path.join(
    tests_dir, "venv"
)
