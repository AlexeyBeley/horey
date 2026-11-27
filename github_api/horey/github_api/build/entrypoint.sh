#!/bin/bash

# Configure the runner
./config.sh \
    --url "https://github.com/${REPO_OWNER}/${REPO_NAME}" \
    --token "${GITHUB_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --unattended \
    --replace

# Start the runner
./run.sh
