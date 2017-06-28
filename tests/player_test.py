"""Player Tests."""

import pytest

from spykeball import player
from spykeball import util

PLAYER_COUNT = 10000


@pytest.fixture(scope='session', params=[PLAYER_COUNT])
def sample_players(count):
    """Return a list of sample players for use in tests."""
    return {
        'players': [player.Player(util.randstring(10)) for _ in range(count)],
        'length': count
        }
