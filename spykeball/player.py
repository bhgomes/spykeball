"""Player Library."""

import json

from spykeball.core import io
from spykeball.core import util
from spykeball.core.exception import InvalidGameException


class Player(util.UIDObject, io.JSONSerializable):
    """An object representing a Spikeball Player."""

    def __init__(self, data, object_uid=None):
        """Initialize Player."""
        if isinstance(data, dict):
            self._name = data.get('name')
            self._stats = data.get('stats')
            object_uid = data.get('UID')
        elif isinstance(data, str):
            self._name = data
            self._stats = {}
        elif isinstance(data, int):
            self._name = ''
            object_uid = data
        else:
            raise TypeError("Data argument Invalid: "
                            "it is neither a string nor a dictionary.", data)
        super().__init__(object_uid)

    def __str__(self):
        """Return name of the player."""
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

    def add_game(self, game, stat_model=None):
        """Add a game to the player's statistics."""
        if game.UID not in self.stats.keys() or not game.stats_saved:
            self._stats[game.UID] = {
                "stat": game.player_stat(self, stat_model=stat_model),
                "model": game.stat_model
            }
        else:
            # consider ignoring this exception
            raise InvalidGameException("Game already Registered.", game)

    def to_json(self, with_stats=False):
        """Encode the object into valid JSON."""
        out = {'UID': self.UID, 'name': self._name}
        if with_stats and self._stats:
            out['stats'] = self._stats
        return out

    def from_json(self, s):
        """Decode the object from valid JSON."""
        return None

    def save(self, fp, with_stats=True):
        """Save a player's progress in a file."""
        super().save(fp, with_stats)

    def load(self, fp, with_stats=True):
        """Load a player's progress from a file."""
        saved = {}
        with open(fp, "r+") as file:
            saved = json.load(file)
            self._name = saved['name']

            if saved['UID'] != self.UID:
                raise Exception()

            if with_stats:
                stats = saved.get('stats')
                if not stats or not isinstance(stats, dict):
                    raise Exception()
                else:
                    self._stats = stats
