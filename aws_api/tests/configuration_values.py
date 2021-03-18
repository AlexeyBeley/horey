import os


class ConfigValues:
    def __init__(self):
        self.aws_api_account = "12345678910"
        ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore")
        self.aws_api_cache_dir = os.path.join(ignore_dir, "cache")
        self.accounts_file = "horey/accounts.py"


def main():
    return ConfigValues()




