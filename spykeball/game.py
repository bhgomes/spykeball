"""Game Package."""

from spykeball.core import util
from spykeball.core.exception import InvalidGameException
from spykeball.core.exception import InvalidPlayerException
from spykeball.stat import player_score


class Game(util.UIDObject):
    """Game Object."""

    def __init__(self, p1, p2, p3, p4, object_uid=None):
        """Initialize Game Object."""
        self.player1 = p1
        self.player2 = p2
        self.player3 = p3
        self.player4 = p4
        self._players = (p1, p2, p3, p4)
        self._action_list = []
        self._gameplayed = False
        self.winner = None
        self.length = None
        super().__init__(object_uid)

    @property
    def action_list(self):
        """Return the action list."""
        return self._action_list

    def __repr__(self):
        """Representation of the Game object."""
        pstring = ", ".join(map(str, self._players))
        return "Game(" + pstring + ")"

    def evaluate(self, player):
        """Evaluate a player based on their performance in the game."""
        if player not in self._players:
            raise InvalidPlayerException("Player is not in this game.",
                                         player, self)
        if not self._gameplayed:
            raise InvalidGameException("Game has not been played yet.", self)
        # calculate their touches to pass into the statistics
        return player_score(player, self)

    def has_been_played(self):
        """Return true if game has been played."""
        return self._gameplayed

    def play(self, *touches):
        """Perform all touches from the game."""
        if not self._gameplayed:
            pass
        return self.winner
