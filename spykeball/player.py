"""Player Library."""

from spykeball.core import io
from spykeball.core import util
from spykeball.core.exception import (
    GameException,
    JSONKeyError,
)


class Player(util.UIDObject, io.JSONSerializable):
    """An object representing a Spikeball Player."""

    def __init__(self, name, object_uid=None):
        """Initialize Player."""
        super().__init__(object_uid)
        self._name = name
        self._stats = {}

    def __str__(self):
        """Return name of the player or UID if name is empty."""
        return self._name if self._name else self.UID

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

    @property
    def games_played(self):
        """Return the games that this person has participated in."""
        return tuple(self._stats.keys())

    def add_game(self, game, stat_model=None):
        """Add a game to the player's statistics."""
        # check this resolution
        if game.UID not in self.stats.keys() or not game.stats_saved:
            self._stats[game.UID] = {
                "stat": game.player_stat(self, stat_model=stat_model),
                "model": game.stat_model
            }
        else:
            # consider ignoring this exception
            raise GameException("Game already Registered.", game)

    def to_json(self, with_stats=False):
        """Encode the object into valid JSON."""
        player = {'UID': self.UID, 'name': self._name}
        if with_stats and self._stats:
            player['stats'] = self._stats
        return player

    @classmethod
    def from_json(cls, data, with_stats=False):
        """Decode the object from valid JSON."""
        player = None
        if util.has_keys(data, 'name', 'UID', error=JSONKeyError):
            player = cls(data['name'], object_uid=data['UID'])

        if with_stats and util.has_keys(data, 'stats', error=JSONKeyError):
            for game_id, stat in data['stats'].items():
                player._stats[game_id] = stat

        return player

    def save(self, fp, with_stats=True):
        """Save a player's progress in a file."""
        super().save(fp, with_stats)

    @classmethod
    def load(cls, fp, with_stats=True):
        """Load a player's progress from a file."""
        super().load(fp, with_stats)
