"""
The entry point script to run authentication.

"""

import json
import argparse


def main(configuration_args):
    """
    Main func

    @return:
    """

    print("Starting evaluation")

    try:
        print(json.loads(configuration_args.jenkins_job_json))
    except Exception as error_instance:
        print(f"Error: {error_instance}")
    print(configuration_args.identity)
    raise RuntimeError("Failed authentication")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jenkins_job_json", type=str)
    parser.add_argument("--identity", type=str)
    _configuration_args = parser.parse_args()
    main(_configuration_args)
