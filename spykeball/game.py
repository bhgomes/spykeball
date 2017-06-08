"""Game Package."""

from spykeball.core import util
from spykeball.core.exception import InvalidGameException
from spykeball.core.exception import InvalidPlayerException
from spykeball.touch import ActionList


class Game(util.UIDObject):
    """Game Object."""

    def __init__(self, p1, p2, p3, p4, stat_model, *actions, object_uid=None):
        """Initialize Game Object."""
        super().__init__(object_uid)
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._players = {"p1": p1, "p2": p2, "p3": p3, "p4": p4}
        self._stat_model = stat_model
        self._action_list = None
        self._game_played = False
        self._winner = (None, None)
        self._length = 0
        self._stats = {p1: None, p2: None, p3: None, p4: None}
        self._stats_calculated = False

        if len(actions) != 0:
            self.play(*actions)

    def __repr__(self):
        """Representation of the Game object."""
        pstring = ", ".join(map(str, list(self._players.values())))
        return "Game(" + pstring + ")"

    def __len__(self):
        """Return length of the game."""
        return self._length

    def _verify_play_status(self, error_on=False):
        """Verify that the game is played or not."""
        if error_on:
            if self._game_played:
                raise InvalidGameException("Game has already been played.",
                                           self)
        else:
            if not self._game_played:
                raise InvalidGameException("Game has not been played yet.",
                                           self)

    @property
    def stat_model(self):
        """Return the stat model of the game."""
        return self._stat_model

    @stat_model.setter
    def stat_model(self, new_stat_model):
        """Set the stat model."""
        self._stat_model = new_stat_model

    @property
    def players(self):
        """Return players of the game."""
        return self._players

    @property
    def action_list(self):
        """Return the action list."""
        return self._action_list

    @action_list.setter
    def action_list(self, *touches):
        """Set the action list."""
        self.play(*touches)

    @property
    def played(self):
        """Return true if game has been played."""
        return self._game_played

    @property
    def winner(self):
        """Return the winner of the game."""
        return self._winner

    @property
    def length(self):
        """Return length of game."""
        return self._length

    def player_stat(self, player, stat_model=None):
        """Evaluate a player based on their performance in the game."""
        self._verify_play_status(error_on=False)

        if stat_model is not None:
            self._stat_model = stat_model
            self._stats_calculated = False

        if not self._stats_calculated:
            self._stats = stat_model(self._action_list)

        stat = self._stats.get(player)

        if stat is None:
            raise InvalidPlayerException("Player is not in this game.",
                                         player, self)
        return stat

    def play(self, *touches):
        """Perform all touches from the game."""
        self._verify_play_status(error_on=True)

        self._action_list = ActionList(
            self._p1, self._p2, self._p3, self._p4, *touches)
        self._game_played = True
        return self._winner

    def save(self, file=None):
        """Save the Game data to a file."""
        self._verify_play_status(error_on=False)
        raise NotImplemented("Not yet implemented")

    def reset(self):
        """Reset the game and recalls all scores from players."""
        raise NotImplemented("Not yet implemented")


class GameFile(object):
    """Represent a Game as a file."""
