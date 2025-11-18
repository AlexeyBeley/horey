"""
Testing selenium api
"""
from pathlib import Path

import pytest
from horey.selenium_api.aucton_api import AuctionAPI
from horey.selenium_api.server import Server

auction_api = AuctionAPI()

#print(os.path.abspath(sys.modules[AuctionAPI.__module__].__file__))
# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_app_run():
    Server().run()


@pytest.mark.unit
def test_update_info_auction_event_id():
    server = Server()
    server.update_info(auction_event_id=19)


@pytest.mark.unit
def test_update_info_provider_id():
    server = Server()
    server.update_info(provider_id=1)


@pytest.mark.unit
def test_load_reports():
    server = Server()
    ret = server.load_reports()
    assert ret


@pytest.mark.wip
def test_run_server():
    """

    Server.self.html_dir_path = Path(__file__).parent / "html"
    Server.self.report_html_template_name = "report_page_sample.html"
    with open(Server.self.html_dir_path / Server.self.report_html_template_name, encoding="utf-8") as file_handler:
        report_html = file_handler.read()

    Server.self.load_report = lambda x: report_html

    :return:
    """

    server = Server()
    server.run()

