import os


class ConfigValues:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.aws_api_account = "12345678910"
        ignore_dir = os.path.join(current_dir, "ignore")
        self.aws_api_cache_dir = os.path.join(ignore_dir, "cache")
        self.accounts_file = os.path.join(
            current_dir, "accounts", "default_managed_account.py"
        )


def main():
    return ConfigValues()
