"""Game Package."""

__all__ = ['Team', 'GameException', 'Game']

from collections import namedtuple

from . import io
from . import util
from . import touch

from .io import JSONKeyError
from .player import PlayerException
from .touch import TouchMapException

from .player import Player, PlayerMap
from .model import StatModel, DefaultStatModel


Team = namedtuple('Team', ['p1', 'p2'])


class GameException(Exception):
    """Raise an exception about a game."""


class Game(util.UIDObject, io.JSONSerializable):
    """Game Object."""

    def __init__(self, p1, p2, p3, p4,
                 actions=None,
                 stat_model=DefaultStatModel,
                 object_uid=None,
                 autoplay=False):
        """Initialize Game Object."""
        self.players = p1, p2, p3, p4
        self._stat_model = stat_model
        # convert to defaultdict?
        self._stats = {
            p1: None, p2: None, p3: None, p4: None,
            'score': {'home': None, 'away': None}, 'winner': None
        }
        self.actions = actions
        self._index = 0

        super().__init__(object_uid)

        if autoplay:
            self.play()

    def __str__(self):
        """String Representation of the Game."""
        return "Game(\n\n({} and {}) vs ({} and {})\n\n)".format(
            self.p1, self.p2, self.p3, self.p4)

    def __iter__(self):
        """Return iterator object for Game."""
        return self

    def __next__(self):
        """Return the next item in the iterator."""
        try:
            next_point = self._actionlist[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return next_point

    def __len__(self):
        """Return length of the game."""
        return len(self._actionlist) if self._actionlist else 0

    def __contains__(self, item):
        """Check if player is in the game or if touchmap is in the game."""
        if isinstance(item, Player):
            return item in self._players
        elif isinstance(item, str):
            return (self._actionlist_strings
                    and item in self._actionlist_strings)
        elif isinstance(item, touch.Touch):
            return self._actionlist and item in self._actionlist
        else:
            return False

    def __getitem__(self, index):
        """Get the item given by the index."""
        if isinstance(index, Player):
            if not self._actionlist:
                raise TouchMapException("TouchMap is not parsed.")
            if index not in self._players.values():
                raise PlayerException("Player '{}' not in Game.".format(index))
            participant_actions = {'actor': [], 'target': []}
            for play in self._actionlist:
                for action in play:
                    if action.actor == index:
                        participant_actions['actor'].append(action)
                    if action.target == index:
                        participant_actions['target'].append(action)
            return participant_actions
        elif isinstance(index, str):
            if index in ('p1', 'p2', 'p3', 'p4'):
                return self._players[index]
            elif index in self._actionlist_strings:
                return self._actionlist[self._actionlist_strings.index(index)]
            else:
                raise IndexError("Object '{}' not in Game.".format(index))
        elif isinstance(index, int):
            if self._actionlist:
                return self._actionlist[index]
            else:
                raise TouchMapException("TouchMap is not parsed.")
        else:
            raise IndexError("Object '{}' not in Game.".format(index))

    def __setitem__(self, index, value):
        """Set the item given by the index to the given value."""
        if isinstance(index, Player):
            raise NotImplementedError("IDK")
        elif isinstance(index, str):
            util.typecheck(value, Player)
            if index in ('p1', 'p2', 'p3', 'p4'):
                old_actions = self[self._players[index]]
                for play in old_actions['actor']:
                    for action in play:
                        action.actor = value
                for play in old_actions['target']:
                    for action in play:
                        action.target = value
                self._players[index] = value
            else:
                raise IndexError("Object '{}' not in Game.".format(index))
        elif isinstance(index, int):
            if isinstance(value, str):
                self._actionlist[index] = touch.parse_point(value,
                                                            self._players)
                self._actionlist_strings[index] = value
            elif isinstance(value, touch.Touch):
                self._actionlist[index] = value
                # self._actionlist_strings[index] = touch.unparse_point(value)
                raise NotImplementedError("IDK")
            else:
                raise util.default_typeerror(value, str, touch.Touch)
        else:
            raise util.default_typeerror(index, int, str, Player)

    def _reset_game_flags(self):
        """Reset the game flags."""
        self._played = False
        self._stats_calculated = False
        self._stats_saved = False

    @property
    def p1(self):
        """Return Player 1."""
        return self._players['p1']

    @p1.setter
    def p1(self, other):
        """Set Player 1."""
        self._players['p1'] = other

    @property
    def p2(self):
        """Return Player 2."""
        return self._players['p2']

    @p2.setter
    def p2(self, other):
        """Set Player 2."""
        self._players['p2'] = other

    @property
    def p3(self):
        """Return Player 3."""
        return self._players['p3']

    @p3.setter
    def p3(self, other):
        """Set Player 3."""
        self._players['p3'] = other

    @property
    def p4(self):
        """Return Player 4."""
        return self._players['p4']

    @p4.setter
    def p4(self, other):
        """Set Player 4."""
        self._players['p4'] = other

    @property
    def players(self):
        """Return players of the game."""
        return self._players

    @players.setter
    def players(self, ps):
        """Set the players."""
        util.typecheck(ps, list, tuple, dict)
        if isinstance(ps, (list, tuple)) and len(ps) == 4:
            self._players = dict(zip(('p1', 'p2', 'p3', 'p4'), ps))
        elif util.haskeys(ps, 'p1', 'p2', 'p3', 'p4', error=JSONKeyError):
            self._players = ps

    @property
    def home_team(self):
        """Return home team of the game."""
        return Team(p1=self._players['p1'], p2=self._players['p2'])

    @home_team.setter
    def home_team(self, other):
        """Set the home team."""
        self._players['p1'] = other[0]
        self._players['p2'] = other[1]

    @property
    def away_team(self):
        """Return away team of the game."""
        return Team(p1=self._players['p3'], p2=self._players['p4'])

    @away_team.setter
    def away_team(self, other):
        """Set the away team."""
        self._players['p3'] = other[0]
        self._players['p4'] = other[1]

    @property
    def stat_model(self):
        """Return the stat model of the game."""
        return self._stat_model

    @stat_model.setter
    def stat_model(self, other):
        """Set the stat model."""
        self._stat_model = other
        self._stats_calculated = False

    @property
    def actions(self):
        """Return the action list."""
        return self._actionlist

    @actions.setter
    def actions(self, other):
        """Set the action list."""
        util.typecheck(other, list, tuple, type(None))
        if util.isinnertype(other, str):
            self._actionlist_strings = other
            other = touch.parse(other, self._players)
            self._parsed = True
        elif util.isinnertype(other, touch.Touch):
            for play in other:
                for action in play:
                    if (action.actor not in self._players.values()
                            or action.target not in self._players.values()):
                        raise TouchMapException(
                            "Player Mismatch. TouchMap has players "
                            "that are not in '{}'.".format(self))
            self._parsed = True
        elif other is None:
            self._parsed = False
        else:
            raise util.default_typeerror(other, list, tuple, type(None))
        self._actionlist = other
        self._reset_game_flags()

    @property
    def played(self):
        """Return true if game has been played."""
        return self._played

    @property
    def stats_calculated(self):
        """Return true if the stats have been calculated."""
        return self._stats_calculated

    @property
    def stats_saved(self):
        """Return true if the stats have been saved."""
        return self._stats_saved

    @property
    def parsed(self):
        """Return true if the touches of the game are parsed."""
        return self._parsed

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
        if len(touches) == 1:
            if touches[0] is None:
                raise util.default_typeerror(touches[0], tuple, list)
            self.actions = touches[0]
        elif len(touches) > 1:
            self.action = touches
        elif self._played and self._stats_saved:
            raise GameException("Game has already been played with "
                                "these touches.", self._actionlist_strings)

        if not self._played:
            if self._actionlist is None:
                raise GameException("No touches registered.", self)

            service = self.home_team
            other = self.away_team
            score = {service: 0, other: 0}

            for action in self:
                if action[0].actor not in service:
                    raise TouchMapException("Wrong team serving.",
                                            action, self._actionlist)
                player = action[-1].actor
                success = action[-1].success

                if ((success and player not in service)
                        or (not success and player in service)):
                    service, other = other, service
                score[service] += 1

            self._stats['winner'] = (service if score[service] > score[other]
                                     else other)

            self._stats['score'] = {
                'home': score[self.home_team],
                'away': score[self.away_team]
            }

            self._played = True

        if save_stats and not self._stats_saved:
            for player in self._players.values():
                player.add_game(self, override=True)
            self._stats_saved = True

        return self._stats

    def player_stat(self, player, stat_model=None):
        """Evaluate a player based on their performance in the game."""
        if not self._played:
            raise GameException("Game has not been played yet.", self)

        if stat_model != self._stat_model and stat_model is not None:
            self._stat_model = stat_model
            self._stats_calculated = False

        if not self._stats_calculated:
            self._stats.update(self._stat_model.calculate(self))
            self._stats_calculated = True

        stat = self._stats.get(player)

        if stat is None:
            raise PlayerException("Player is not in this game.", player, self)
        return stat

    def to_json(self, game_played=True, with_stats=True):
        """Encode the object into valid JSON."""
        game = {
            'UID': self.UID,
            'teams': {'home': self.home_team, 'away': self.away_team},
            'actions': self._actionlist_strings
        }

        if game_played and self._played:
            game['winner'] = ("home" if self.winner == self.home_team
                              else "away")

            game['score'] = {
                'home': self.score['home'],
                'away': self.score['away']
            }

            if with_stats:
                game['stats'] = {k: self.player_stat(self._players[k]) for k in
                                 self._players}
                game['stats']['model'] = self._stat_model

        return game

    @classmethod
    def from_json(cls, data, game_played=True, with_stats=True):
        """Decode the object from valid JSON."""
        game = None
        if util.haskeys(data, 'UID', 'teams', 'actions', error=JSONKeyError):
            teams = data['teams']
            if util.haskeys(teams, 'home', 'away', error=JSONKeyError):
                game = cls(
                    Player.from_json(teams['home'][0]),
                    Player.from_json(teams['home'][1]),
                    Player.from_json(teams['away'][0]),
                    Player.from_json(teams['away'][1]),
                    actions=data['actions'],
                    stat_model=DefaultStatModel,
                    object_uid=data['UID']
                    )

                if game_played and util.haskeys(data, 'winner', 'score',
                                                error=JSONKeyError):
                    game._stats['winner'] = data['winner']
                    game._stats['score'] = data['score']

                    if with_stats and util.haskeys(data, 'stats',
                                                   error=JSONKeyError):
                        if util.haskeys(data['stats'], 'p1', 'p2', 'p3', 'p4',
                                        'model', error=JSONKeyError):
                            game.stat_model = StatModel.from_json(
                                data['stats']['model'])
        return game

    def save(self, fp, game_played=True, with_stats=True):
        """Save the Game data to a file."""
        super().save(fp, game_played, with_stats)

    @classmethod
    def load(self, fp, game_played=True, with_stats=True):
        """Load the Game data from a file."""
        return super().load(fp, game_played, with_stats)


class GameRegistry(object):
    """Class that holds game objects and records their history."""
