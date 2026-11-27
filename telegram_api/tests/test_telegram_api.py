import pytest
from horey.telegram_api.telegram_api import TelegramAPI

telegram_api = TelegramAPI(token = "")

@pytest.mark.wip
def test_init_api():
    """
    Parse get/post request.

    :return:
    """

    ret = telegram_api.start()
    assert len(ret) > 0

