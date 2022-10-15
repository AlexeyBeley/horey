"""
The entry point script to run authentication.

"""

import json
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jenkins_job_json", type=str)
    configuration_args = parser.parse_args()
    print(json.loads(configuration_args.jenkins_job_json))
