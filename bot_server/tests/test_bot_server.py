"""
Testing Bot Server
"""

import pytest

from horey.bot_server.bot_server import BotServer


# pylint: disable= missing-function-docstring
@pytest.fixture(name="bot_server")
def fixture_bot_server():
    """
    Test Bot Server initiation
    @return:
    """

    bot_server = BotServer()
    yield bot_server


@pytest.mark.wip
def test_create_rule_raw(bot_server):
    bot_server.start()
