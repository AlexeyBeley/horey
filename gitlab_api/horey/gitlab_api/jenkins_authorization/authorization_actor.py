"""
The entry point script to run authentication.

"""

import json
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jenkins_job_json", type=str)
    parser.add_argument("--identity", type=str)
    configuration_args = parser.parse_args()
    try:
        print(json.loads(configuration_args.jenkins_job_json))
    except Exception as error_instance:
        print(f"Error: {error_instance}")
    print(configuration_args.identity)
