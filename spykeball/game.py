"""Game Package."""

import json

from functools import reduce

from spykeball.core import util
from spykeball.core.exception import InvalidGameException
from spykeball.core.exception import InvalidPlayerException
from spykeball.stat import DefaultStatModel
from spykeball.touch import ActionList


class Game(util.UIDObject, util.JSONSerializable):
    """Game Object."""

    def __init__(self, p1, p2, p3, p4,
                 stat_model=DefaultStatModel, *actions, object_uid=None):
        """Initialize Game Object."""
        super().__init__(object_uid)
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._players = {"p1": p1, "p2": p2, "p3": p3, "p4": p4}
        self._teams = {"home": (p1, p2), "away": (p3, p4)}
        self._stat_model = stat_model
        self._game_played = False
        self._stats = {
            p1: None, p2: None, p3: None, p4: None,
            'score': None, 'winner': None
        }
        self._stats_calculated = False
        self._stats_saved = False

        self._set_actionlist(actions)

    def __str__(self):
        """String Representation of the Game."""
        title = "Game({\n\n(%s and %s) vs (%s and %s)" % \
            (self._p1, self._p2, self._p3, self._p4)
        return title + "\n\n})"

    def __len__(self):
        """Return length of the game."""
        return len(self._actionlist)

    def _verify_played_status(self, error_on=False):
        """Verify that the game is played or not."""
        if error_on:
            if self._game_played:
                raise InvalidGameException(
                    "Game has already been played.", self)
        else:
            if not self._game_played:
                raise InvalidGameException(
                    "Game has not been played yet.", self)

    def _set_actionlist(self, touches):
        """Set the ActionList object stored in the Game."""
        if len(touches) == 1 and isinstance(touches[0], ActionList):
            self._actionlist = touches[0]
            self.reset()
        elif isinstance(touches, ActionList):
            self._actionlist = touches
            self.reset()
        elif len(touches) != 0:
            self._actionlist = ActionList(
                self._p1, self._p2, self._p3, self._p4, *touches)
            self.reset()

    @property
    def stat_model(self):
        """Return the stat model of the game."""
        return self._stat_model

    @stat_model.setter
    def stat_model(self, new_stat_model):
        """Set the stat model."""
        self._stat_model = new_stat_model
        self._stats_calculated = False

    @property
    def players(self):
        """Return players of the game."""
        return self._players

    @property
    def home_team(self):
        """Return home team of the game."""
        return self._teams['home']

    @property
    def away_team(self):
        """Return away team of the game."""
        return self._teams['away']

    @property
    def actions(self):
        """Return the action list."""
        return self._actionlist

    @actions.setter
    def actions(self, touches):
        """Set the action list."""
        self._set_actionlist(touches)

    @property
    def played(self):
        """Return true if game has been played."""
        return self._game_played

    @property
    def stats_saved(self):
        """Return true if the stats have been saved."""
        return self._stats_saved

    @property
    def winner(self):
        """Return the winner of the game."""
        return self._stats['winner']

    @property
    def score(self):
        """Return the score of the game."""
        return self._stats['score']

    @property
    def stats(self):
        """Return stats of the game."""
        return self._stats

    def play(self, *touches, save_stats=True):
        """Perform all touches from the game."""
        if self._game_played and self._stats_saved:
            raise InvalidGameException("Game has already been played.", self)

        if not self._game_played:
            self._set_actionlist(touches)

            if self._actionlist is None:
                raise InvalidGameException("No touches registered.", self)

            score = {
                self._teams['home']: 0,
                self._teams['away']: 0
            }

            service = self._teams['home']
            other = self._teams['away']

            # check that the number of moves follows a certain requirement

            for action in self._actionlist.subaction_groups():
                if action[0].actor not in service:
                    raise InvalidGameException("Wrong team serving", self)

                player = action[-1].actor
                success = action[-1].success

                if (success and player not in service) or \
                        (not success and player in service):
                    service, other = other, service

                score[service] += 1

            self._stats['winner'] = \
                service if score[service] > score[other] else other

            self._stats['score'] = {
                "home": score[self._teams['home']],
                "away": score[self._teams['away']]
            }

            self._game_played = True

        if save_stats and not self._stats_saved:
            for player in self._players.values():
                player.add_game(self)
            self._stats_saved = True

        return self._stats

    def player_stat(self, player, stat_model=None):
        """Evaluate a player based on their performance in the game."""
        self._verify_played_status(error_on=False)
        # fix this

        if stat_model is not None:
            self._stat_model = stat_model
            self._stats_calculated = False

        if not self._stats_calculated:
            self._stats = {
                **self._stats,
                **self._stat_model.calculate(self._actionlist)
            }
            self._stats_calculated = True

        stat = self._stats.get(player)

        if stat is None:
            raise InvalidPlayerException("Player is not in this game.",
                                         player, self)
        return stat

    def to_json(self):
        """Encode the object into valid JSON."""
        return {"class": "Game", "UID": self.UID}

    def from_json(self, s):
        """Decode the object from valid JSON."""
        return None

    def save(self, filepath, with_stats=True):
        """Save the Game data to a file."""
        self._verify_played_status(error_on=False)

        saved = {
            "game": self,
            "teams": {
                "home": self._teams['home'],
                "away": self._teams['away']
            },
            "winner": "home" if self._teams['home'] is
            self._stats['winner'] else "away",
            "score": {
                "home": self._stats['score']['home'],
                "away": self._stats['score']['away']
            },
            "actionlist": self._actionlist.as_strings
        }

        if with_stats:
            saved["stats"] = {k: self.player_stat(self._players[k]) for k in
                              self._players}
            saved["stats"]["model"] = self._stat_model

        with open(filepath, "w+") as file:
            json.dump(
                saved, file, default=util.JSONSerializable.serialize, indent=4)

    def load(self, filepath):
        """Load the Game data from a file."""
        saved = {}
        with open(filepath, "r+") as file:
            saved = json.load(
                reduce(lambda x, y: x + "\n" + y, file.readlines))
        self._actionlist = saved['actionlist']

    def reset(self):
        """Reset the game and recalls all scores from players."""
        self._game_played = False
        self._stats_calculated = False
        self._stats_saved = False


class GameFile(object):
    """Represent a Game as a file."""
