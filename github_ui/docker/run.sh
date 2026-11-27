#!/bin/bash
# Container entry point:
#   1. Downloads the GitHub API and Postgres API configurations (they hold the token and the password)
#      from AWS Secrets Manager with the horey infrastructure_api secrets_api actor, each to the path set in
#      github_api_configuration_file_path / postgres_api_configuration_file_path of the GitHub UI configuration
#      (GITHUB_UI_CONFIGURATION_FILE_PATH).
#   2. Runs the command passed as arguments (e.g. the alembic migrations), if any.
#      Otherwise starts horey.github_ui.server.
#
# Environment:
#   GITHUB_UI_CONFIGURATION_FILE_PATH             required, set by the Dockerfile.
#   GITHUB_API_CONFIGURATION_SECRET_NAME          required, AWS Secrets Manager secret holding the GitHub API configuration.
#   GITHUB_API_CONFIGURATION_SECRET_REGION        required, region of that secret.
#   POSTGRES_API_CONFIGURATION_SECRET_NAME        required, AWS Secrets Manager secret holding the Postgres API configuration.
#   POSTGRES_API_CONFIGURATION_SECRET_REGION      optional, region of that secret. Default: GITHUB_API_CONFIGURATION_SECRET_REGION.
#   AWS credentials (AWS_ACCESS_KEY_ID etc. or an instance/task role) must be available.

set -euo pipefail

: "${GITHUB_UI_CONFIGURATION_FILE_PATH:?GITHUB_UI_CONFIGURATION_FILE_PATH must be set}"
: "${GITHUB_API_CONFIGURATION_SECRET_NAME:?GITHUB_API_CONFIGURATION_SECRET_NAME must be set}"
: "${GITHUB_API_CONFIGURATION_SECRET_REGION:?GITHUB_API_CONFIGURATION_SECRET_REGION must be set}"
: "${POSTGRES_API_CONFIGURATION_SECRET_NAME:?POSTGRES_API_CONFIGURATION_SECRET_NAME must be set}"
POSTGRES_API_CONFIGURATION_SECRET_REGION="${POSTGRES_API_CONFIGURATION_SECRET_REGION:-${GITHUB_API_CONFIGURATION_SECRET_REGION}}"

# The secrets hold a token and a password: readable by the owner only.
umask 077

# download_secret <secret name> <secret region> <GitHub UI configuration key holding the destination file path>
download_secret() {
    local secret_name="$1" secret_region="$2" configuration_key="$3" file_path

    file_path="$(python -c '
import json, sys
configuration = json.load(open(sys.argv[1], encoding="utf-8"))
if sys.argv[2] not in configuration:
    sys.exit(f"{sys.argv[2]} is not defined in {sys.argv[1]}")
print(configuration[sys.argv[2]])
' "${GITHUB_UI_CONFIGURATION_FILE_PATH}" "${configuration_key}")"
    mkdir -p "$(dirname "${file_path}")"

    echo "Downloading secret '${secret_name}' to '${file_path}'"
    python -m horey.infrastructure_api.secrets_api_actor \
        --action get_secret_file \
        --secret_name "${secret_name}" \
        --secret_file_path "${file_path}" \
        --region "${secret_region}"
}

download_secret "${GITHUB_API_CONFIGURATION_SECRET_NAME}" "${GITHUB_API_CONFIGURATION_SECRET_REGION}" github_api_configuration_file_path
download_secret "${POSTGRES_API_CONFIGURATION_SECRET_NAME}" "${POSTGRES_API_CONFIGURATION_SECRET_REGION}" postgres_api_configuration_file_path

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec python -m horey.github_ui.server
