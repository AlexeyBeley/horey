# Horey MCP server image. Same layout as github_ui/docker/Dockerfile: the required horey packages are resolved
# recursively from the requirements.txt files and installed with pip_api_make.py.
#
# HOREY_MCP_PACKAGES - the horey packages whose tools the server exposes (installed together with horey.mcp).
# Only installed packages having horey/<package_name>/mcp_tools.py are loaded.
#
# Build from the horey repository root:
#   docker build -f mcp/docker/Dockerfile -t horey-mcp --build-arg HOREY_MCP_PACKAGES="jenkins_api github_api" .

FROM python:3.14-slim-trixie AS horey_base

# Horey base, see BuildAPI.add_horey_base_to_dockerfile
USER root
RUN apt update
RUN apt install -yqq python3 python3-pip git make wget which findutils
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt-get update && apt-get remove -y python3-packaging && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -yqq --upgrade python3-packaging python3-pip  && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages twine


FROM horey_base AS horey_dependencies

ARG HOREY_MCP_PACKAGES=""

COPY . /horey
RUN test -f /horey/pip_api/horey/pip_api/pip_api_make.py \
    || { echo "ERROR: build context must be the horey repository root: docker build -f mcp/docker/Dockerfile -t horey-mcp <horey repo root>"; exit 1; }
RUN mkdir -p /horey_required \
    && for package_name in mcp ${HOREY_MCP_PACKAGES}; do \
        python /horey/pip_api/horey/pip_api/pip_api_make.py \
            --copy_horey_dependencies \
            --package_name ${package_name} \
            --dst_dir_path /horey_required \
            --pip_api_configuration /horey/pip_api_docker_configuration.py || exit 1; \
    done


FROM horey_base

ARG HOREY_MCP_PACKAGES=""

COPY --from=horey_dependencies /horey_required/horey /horey
#HOREY_REPOS_END

RUN for package_name in mcp ${HOREY_MCP_PACKAGES}; do \
        python /horey/pip_api/horey/pip_api/pip_api_make.py --install horey.${package_name} \
            --pip_api_configuration /horey/pip_api_docker_configuration.py || exit 1; \
    done

# Packages' configuration files (<package_name>_configuration.py|json), mounted read-only at run time.
ENV HOREY_MCP_CONFIGURATIONS_DIR_PATH=/opt/horey/mcp/configurations
ENV HOREY_MCP_HOST=0.0.0.0
ENV HOREY_MCP_PORT=8080

# Not / : the horey repository has an "mcp" directory, it must not shadow the mcp SDK.
WORKDIR /opt/horey/mcp

EXPOSE 8080

ENTRYPOINT ["python", "-m", "horey.mcp.mcp_server"]
