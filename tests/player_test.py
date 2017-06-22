"""Player Tests."""

import pytest

from spykeball import player
from spykeball.core import util


@pytest.fixture(scope='session')
def sample_players():
    """Return a list of sample players for use in tests."""
    length = 10000
    return {
        "players": [player.Player(util.randstring(10)) for _ in range(length)],
        "length": length
        }
