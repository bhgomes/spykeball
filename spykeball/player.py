"""Player Library."""

from spykeball.core import util


class Player(util.UIDObject):
    """An object representing a Spikeball Player."""

    def __init__(self, name, object_uid=None):
        """Initialize player with a name."""
        self.name = name
        self.stats = dict()
        super().__init__(object_uid)

    def add_game(self, game):
        """Add a game to the player's statistics."""
        if game.get_uid() not in self.stats.keys():
            self.stats[game.get_uid()] = game.evaluate(self)

    def __repr__(self):
        """Representation of the Player Object."""
        return "Player(" + str(self.get_uid()) + " : " + self.name + ")"

    def __str__(self):
        """Return name of the player."""
        return self.name
