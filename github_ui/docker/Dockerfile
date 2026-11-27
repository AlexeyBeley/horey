# Mirrors infrastructure_api BuildAPI.prepare_docker_image_horey_package_build_directory:
# the required horey packages are resolved recursively from the requirements.txt files
# and installed with pip_api_make.py. Nothing is hardcoded except the package name.
#
# Build from the horey repository root:
#   docker build -f github_ui/docker/Dockerfile -t horey-github-ui .
#   docker run --rm -p 8080:8080 \
#       -e GITHUB_API_CONFIGURATION_SECRET_NAME=<secret name> \
#       -e GITHUB_API_CONFIGURATION_SECRET_REGION=<region> \
#       -e POSTGRES_API_CONFIGURATION_SECRET_NAME=<secret name> \
#       -e POSTGRES_API_CONFIGURATION_SECRET_REGION=<region> \
#       -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
#       horey-github-ui
#
# The GitHub UI configuration (github_ui_configuration.json) is baked into the image and
# GITHUB_UI_CONFIGURATION_FILE_PATH points to it. It only holds the paths of the GitHub API and Postgres API
# configurations, which hold the token (pat) and the password. Those files are never part of the image: run.sh downloads them from
# AWS Secrets Manager (horey.infrastructure_api.secrets_api_actor) when the container starts, then starts the server.

FROM python:3.14-slim-trixie AS horey_base

# Horey base, see BuildAPI.add_horey_base_to_dockerfile
USER root
RUN apt update
RUN apt install -yqq python3 python3-pip git make wget which findutils
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt-get update && apt-get remove -y python3-packaging && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -yqq --upgrade python3-packaging python3-pip  && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages twine


# Resolve the horey packages github_ui depends on (recursively) and copy only them.
# Equivalent to StandaloneMethods.copy_horey_package_required_packages_to_build_dir.
FROM horey_base AS horey_dependencies

ARG HOREY_PACKAGE=github_ui

COPY . /horey
RUN test -f /horey/pip_api/horey/pip_api/pip_api_make.py \
    || { echo "ERROR: build context must be the horey repository root: docker build -f github_ui/docker/Dockerfile -t horey-github-ui <horey repo root>"; exit 1; }
RUN mkdir -p /horey_required \
    && python /horey/pip_api/horey/pip_api/pip_api_make.py \
        --copy_horey_dependencies \
        --package_name ${HOREY_PACKAGE} \
        --dst_dir_path /horey_required \
        --pip_api_configuration /horey/pip_api_docker_configuration.py


FROM horey_base

ARG HOREY_PACKAGE=github_ui

COPY --from=horey_dependencies /horey_required/horey /horey
#HOREY_REPOS_END

RUN python /horey/pip_api/horey/pip_api/pip_api_make.py --install horey.${HOREY_PACKAGE} --pip_api_configuration /horey/pip_api_docker_configuration.py

# GitHub UI configuration, loaded by server.py from GITHUB_UI_CONFIGURATION_FILE_PATH.
# Its github_api_configuration_file_path and postgres_api_configuration_file_path are where run.sh stores the downloaded configurations.
ARG GITHUB_UI_CONFIGURATION_FILE=github_ui/docker/github_ui_configuration.json
ENV GITHUB_UI_CONFIGURATION_FILE_PATH=/opt/horey/config/github_ui_configuration.json
COPY ${GITHUB_UI_CONFIGURATION_FILE} ${GITHUB_UI_CONFIGURATION_FILE_PATH}

# Entry point: downloads the GitHub API configuration secret, then starts the server.
COPY github_ui/docker/run.sh /opt/horey/run.sh
RUN chmod +x /opt/horey/run.sh

# Alembic migrations, run by "make alembic_migrate": alembic -c /opt/horey/github_ui/alembic.ini upgrade head
COPY github_ui/alembic.ini /opt/horey/github_ui/alembic.ini
COPY github_ui/alembic /opt/horey/github_ui/alembic

EXPOSE 8080

ENTRYPOINT ["/opt/horey/run.sh"]
