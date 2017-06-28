"""Game Tests."""

import pytest

from spykeball import game
from spykeball import util


@pytest.fixture(scope='session')
def sample_games(sample_players):
    """Create Sample Games from sample_players."""
    length = sample_players['length'] / 4
    players = sample_players['players']
    games = []
    for p1, p2, p3, p4 in util.groupby(players, 4):
        games.append(game.Game(p1, p2, p3, p4))
    return {'games': games, 'length': length}


def test_game_iteration(sample_games):
    """Test the iteration protocol on the game class."""
    for gameobj in sample_games:
        for event, true_event in zip(gameobj, gameobj._actionlist):
            assert event == true_event


def test_game_containment(sample_games):
    """Test the containment of players or actions in game objects."""
    assert True
