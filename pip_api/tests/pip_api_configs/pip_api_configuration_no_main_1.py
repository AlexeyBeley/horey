"""
Pip api configuration
"""
import os

tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
multi_package_repositories = {"horey.":
            os.path.dirname(os.path.dirname(tests_dir))
        }
