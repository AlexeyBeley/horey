"""
FastAPI HTTP server: health check and dashboard.
"""

import os
import traceback
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from horey.github_ui.github_ui import GithubUI
from horey.github_ui.github_ui_configuration_policy import GithubUIConfigurationPolicy
from horey.h_logger import get_logger

logger = get_logger()

HOST = "0.0.0.0"
PORT = 8080

GITHUB_UI_CONFIGURATION_FILE_PATH_ENV = "GITHUB_UI_CONFIGURATION_FILE_PATH"

DASHBOARD_HTML = (Path(__file__).parent / "html" / "dashboard.html").read_text(encoding="utf-8")

app = FastAPI()

_github_ui = None


def get_github_ui() -> GithubUI:
    """
    Lazy GithubUI. Configured from the file in GITHUB_UI_CONFIGURATION_FILE_PATH (.json or .py),
    which in turn defines github_api_configuration_file_path.

    :return:
    """

    global _github_ui  # pylint: disable=global-statement
    if _github_ui is None:
        configuration = GithubUIConfigurationPolicy()
        if configuration_file_path := os.environ.get(GITHUB_UI_CONFIGURATION_FILE_PATH_ENV):
            configuration.configuration_file_full_path = configuration_file_path
            configuration.init_from_file()
        _github_ui = GithubUI(configuration)
    return _github_ui


def log_exception(message: str):
    """
    Log the error being handled with its full traceback.
    The horey logger formatter drops exc_info and flattens new lines, so the traceback is printed to stderr as is.

    :param message:
    :return:
    """

    logger.error(f"{message}: {traceback.format_exc().splitlines()[-1]}")
    traceback.print_exc()


@app.get("/health-check", response_class=PlainTextResponse)
def health_check():
    """
    Respond 200 OK.

    :return:
    """

    return "ok"

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """
    Present dashboard

    :return:
    """

    return DASHBOARD_HTML


@app.get("/fetch_repos")
def fetch_repos():
    """
    Names of all the repositories under the configured owner (organization).

    :return:
    """

    try:
        return get_github_ui().fetch_repositories()
    except ValueError as error:
        log_exception("GitHub UI is not configured")
        raise HTTPException(status_code=503, detail=f"GitHub UI is not configured: {error}") from error
    except Exception as error:
        log_exception("Failed to fetch repositories")
        raise HTTPException(status_code=502, detail=f"Failed to fetch repositories: {error}") from error


@app.get("/fetch_workflows")
def fetch_workflows(repository: str):
    """
    Names of the workflows of the repository.

    :param repository: Repository name.
    :return:
    """

    try:
        return get_github_ui().fetch_workflows(repository)
    except ValueError as error:
        log_exception("GitHub UI is not configured")
        raise HTTPException(status_code=503, detail=f"GitHub UI is not configured: {error}") from error
    except Exception as error:
        log_exception(f"Failed to fetch workflows of {repository}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch workflows: {error}") from error


class MonitoredRepository(BaseModel):
    """
    A repository with its checked workflows.
    """

    repository: str
    workflows: list[str]


class MonitoredRepositories(BaseModel):
    """
    Request body of /add_to_monitored and /remove_from_monitored.
    """

    repositories: list[MonitoredRepository]


@app.post("/add_to_monitored")
def add_to_monitored(monitored: MonitoredRepositories):
    """
    Add the workflows of the repositories to the monitored_workflows table.

    :param monitored:
    :return:
    """

    workflows_by_repository = {}
    for item in monitored.repositories:
        logger.info(f"Adding to monitored: {item.repository}: {item.workflows}")
        workflows_by_repository.setdefault(item.repository, []).extend(item.workflows)

    try:
        get_github_ui().add_monitored_workflows(workflows_by_repository)
    except ValueError as error:
        log_exception("GitHub UI is not configured")
        raise HTTPException(status_code=503, detail=f"GitHub UI is not configured: {error}") from error
    except Exception as error:
        log_exception("Failed to add to monitored")
        raise HTTPException(status_code=502, detail=f"Failed to add to monitored: {error}") from error
    return {"added": monitored.repositories}


@app.post("/remove_from_monitored")
def remove_from_monitored(monitored: MonitoredRepositories):
    """
    Remove repositories workflows from monitored. For now only logs them.

    :param monitored:
    :return:
    """

    for item in monitored.repositories:
        logger.info(f"Removing from monitored: {item.repository}: {item.workflows}")
    return {"removed": monitored.repositories}


@app.post("/start_monitoring")
def start_monitoring():
    """
    The dashboard started monitoring: from now on it polls /update_monitoring_status. For now only logs.

    :return:
    """

    logger.info("Monitoring started")
    return {"monitoring": True}


@app.post("/stop_monitoring")
def stop_monitoring():
    """
    The dashboard stopped monitoring: it does not poll /update_monitoring_status anymore. For now only logs.

    :return:
    """

    logger.info("Monitoring stopped")
    return {"monitoring": False}


@app.get("/update_monitoring_status")
def update_monitoring_status():
    """
    Current status of the monitored workflows.

    :return: [{"repository": ..., "workflow": ..., "status": ...}]
    """

    try:
        return get_github_ui().get_monitored_workflows_status()
    except ValueError as error:
        log_exception("GitHub UI is not configured")
        raise HTTPException(status_code=503, detail=f"GitHub UI is not configured: {error}") from error
    except Exception as error:
        log_exception("Failed to get the monitoring status")
        raise HTTPException(status_code=502, detail=f"Failed to get the monitoring status: {error}") from error


def main():
    """
    Start the server.

    :return:
    """

    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
