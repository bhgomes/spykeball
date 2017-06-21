"""Game Package."""

from spykeball.core import io
from spykeball.core import util
from spykeball.core.exception import (
    GameException,
    JSONKeyError,
    PlayerException,
    TouchMapException,
)
from spykeball.player import Player
from spykeball.stat.model import StatModel, DefaultStatModel
from spykeball.action.actionlist import ActionList


class Game(util.UIDObject, util.PlayerInterface, io.JSONSerializable):
    """Game Object."""

    def __init__(self, p1, p2, p3, p4, *actions, stat_model=DefaultStatModel,
                 object_uid=None):
        """Initialize Game Object."""
        super().__init__(p1=p1, p2=p2, p3=p3, p4=p4, object_uid=object_uid)

        self._stat_model = stat_model
        self._stats = {
            p1: None, p2: None, p3: None, p4: None,
            'score': {'home': None, 'away': None}, 'winner': None
        }

        self._set_actionlist(actions)

    def __str__(self):
        """String Representation of the Game."""
        return "Game({\n\n({} and {}) vs ({} and {})\n\n})".format(
            self._p1, self._p2, self._p3, self._p4)

    def __len__(self):
        """Return length of the game."""
        return len(self._actionlist)

    def _set_actionlist(self, touches):
        """Set the ActionList object stored in the Game."""
        if len(touches) == 1 and isinstance(touches[0], ActionList):
            if not touches[0].parsed:
                touches[0].register_players(self._players)
            self._actionlist = touches[0]
        elif isinstance(touches, ActionList):
            if not touches.parsed:
                touches.register_players(self._players)
            self._actionlist = touches
        elif len(touches) != 0:
            self._actionlist = ActionList(
                self._p1, self._p2, self._p3, self._p4, *touches)
        else:
            raise TypeError("Touches does not have the correct input type.",
                            touches, type(touches))
        self.reset_game_flags()

    def _verify_played_status(self, error_on=False):
        """Verify that the game is played or not."""
        if error_on:
            if self._game_played:
                raise GameException("Game has already been played.", self)
        else:
            if not self._game_played:
                raise GameException("Game has not been played yet.", self)

    def reset_game_flags(self):
        """Reset the game flags."""
        self._game_played = False
        self._stats_calculated = False
        self._stats_saved = False

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
    def stats_calculated(self):
        """Return true if the stats have been calculated."""
        return self._stats_calculated

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
        # what if they want to play again but with different touches
        # check if touches are different from other touches

        if self._game_played and self._stats_saved:
            raise GameException("Game has already been played.", self)

        if not self._game_played:

            if len(touches) > 0:
                self._set_actionlist(touches)

            if self._actionlist is None:
                raise GameException("No touches registered.", self)

            score = {
                self._teams['home']: 0,
                self._teams['away']: 0
            }

            service = self._teams['home']
            other = self._teams['away']

            # check that the number of moves follows a certain requirements

            for action in self._actionlist.subaction_groups():
                if action[0].actor not in service:
                    raise TouchMapException(
                        "Wrong team serving.", action,  self._actionlist)

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
            raise PlayerException("Player is not in this game.", player, self)
        return stat

    def to_json(self, game_played=True, with_stats=True):
        """Encode the object into valid JSON."""
        game = {
            "UID": self.UID,
            "teams": {
                "home": self._teams['home'],
                "away": self._teams['away']
            },
            "actions": self._actionlist.as_strings
        }

        if game_played and self.played:
            if self._stats['winner'] is self._teams['home']:
                game['winner'] = "home"
            else:
                game['winner'] = "away"

            game['score'] = {
                "home": self._stats['score']['home'],
                "away": self._stats['score']['away']
            }

            if with_stats:
                game["stats"] = {k: self.player_stat(self._players[k]) for k in
                                 self._players}
                game["stats"]["model"] = self._stat_model

        return game

    @classmethod
    def from_json(cls, data, game_played=True, with_stats=True):
        """Decode the object from valid JSON."""
        game = None
        if util.has_keys(data, 'UID', 'teams', 'actions', error=JSONKeyError):
            teams = data['teams']
            if util.has_keys(teams, 'home', 'away', error=JSONKeyError):
                p1 = Player.from_json(teams['home'][0])
                p2 = Player.from_json(teams['home'][1])
                p3 = Player.from_json(teams['away'][0])
                p4 = Player.from_json(teams['away'][1])

                game = cls(p1, p2, p3, p4, DefaultStatModel, data['actions'],
                           object_uid=data['UID'])

                if game_played and util.has_keys(data, 'winner', 'score',
                                                 error=JSONKeyError):
                    game._stats['winner'] = data['winner']
                    game._stats['score'] = data['score']

                    if with_stats and util.has_keys(data, 'stats',
                                                    error=JSONKeyError):
                        if util.has_keys(data['stats'], 'model',
                                         'p1', 'p2', 'p3', 'p4',
                                         error=JSONKeyError):
                            # Stats are ignored because they are calculated
                            # using the given model when requested.
                            game.stat_model = \
                                StatModel.from_json(data['stats']['model'])

        return game

    def save(self, fp, game_played=True, with_stats=True):
        """Save the Game data to a file."""
        super().save(fp, game_played, with_stats)

    @classmethod
    def load(self, fp, *delimeters, action_only=False, game_played=True,
             with_stats=True):
        """Load the Game data from a file."""
        if action_only:
            if isinstance(self, type):
                raise Exception("GOTTA FIGURE THIS OUT OMG.")
            with open(fp, "r+") as file:
                self._actionlist = \
                    [s for s in io.readsplit(file, ",", "\n", *delimeters)
                     if s != '']
                self.reset_game_flags()
        else:
            game = super().load(fp, game_played, with_stats)
        return game


class GameRegistry(object):
    """Class that holds game objects and records their history."""
