"""Player Library."""

from spykeball.core import util
from spykeball.core.exception import InvalidGameException


class Player(util.UIDObject):
    """An object representing a Spikeball Player."""

    def __init__(self, name, object_uid=None):
        """Initialize player with a name."""
        super().__init__(object_uid)
        self._name = name
        self._stats = dict()

    def __repr__(self):
        """Representation of the Player Object."""
        return "Player(" + str(self.UID) + " : " + self._name + ")"

    def __str__(self):
        """Return name of the player."""
        return self._name

    @property
    def name(self):
        """Return name of the player."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set the players name."""
        self._name = new_name

    @property
    def stats(self):
        """Return stats dictionary of the player."""
        return self._stats

    def add_game(self, game, stat_model=None):
        """Add a game to the player's statistics."""
        if game.get_uid() not in self.stats.keys():
            self._stats[game.UID] = {
                "stat": game.player_stat(self, stat_model=stat_model),
                "model": game.stat_model
            }
        else:
            raise InvalidGameException("Game already Registered.", game)

    def save(self, file):
        """Save a player's progress in a file."""
        pass
