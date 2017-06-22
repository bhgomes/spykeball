"""Game Tests."""

import pytest

from spykeball import game


@pytest.fixture(scope='session')
def sample_games(sample_players):
    """Create Sample Games from sample_players."""
    length = sample_players['length'] / 4
    players = sample_players['players']
    games = [game.Game()]
    return {"games": games, "length": length}
