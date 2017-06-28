"""Statistics Modeling Module."""

__all__ = ['StatModel', 'DefaultStatModel']

from abc import ABCMeta, abstractmethod
from collections import defaultdict

from . import io
from . import util

from .io import JSONKeyError
from .player import PlayerException
from .touch import TouchException

from .touch import Defense, Set, Spike, Service


class StatModel(io.JSONSerializable, metaclass=ABCMeta):
    """Interpret a game."""

    __stat_model_registry = {}

    def __new__(cls, name, bases, attr):
        """Add class to the StatModel registry after creation."""
        model = StatModel.__stat_model_registry.get(name)
        if model is None:
            StatModel.__stat_model_registry[name] = cls
        else:
            # think about this
            raise NameError("No two StatModels can have the same name.", name)
        return super().__new__(name, bases, attr)

    @staticmethod
    def touch_components(game, player):
        """Return the relevant touch_components for each player."""
        actions = game[player]

        if actions is None:
            raise PlayerException("Player is not part of the Game.",
                                  player, game)

        performed = actions.get('actor')
        recieved = actions.get('target')

        count = defaultdict(int)

        for act in performed:
            if isinstance(act, Service):
                if act.success:
                    count['serves_made'] += 1
                    if act.is_ace:
                        count['aces'] += 1
                count['serve_total'] += 1
            elif isinstance(act, Defense):
                if act.success:
                    count['d_touch_r'] += 1
                else:
                    count['d_touch_nr'] += 1
                if act.strength == 'w':
                    count['tough_touch'] += 1
            elif isinstance(act, Set):
                if not act.success:
                    count['missed_sets'] += 1
                if act.strength == 'w':
                    count['tough_touch'] += 1
            elif isinstance(act, Spike):
                if act.success:
                    count['spikes_returned'] += 1
                else:
                    count['missed_spikes'] += 1
                count['spike_total'] += 1
            else:
                raise TouchException("Action must be a subtype of Touch.", act)

        for act in recieved:
            if isinstance(act, Service):
                if act.is_ace:
                    count['aced'] += 1
            elif isinstance(act, Defense):
                pass
            elif isinstance(act, Set):
                pass
            elif isinstance(act, Spike):
                pass
            else:
                raise TouchException("Action must be a subtype of Touch.", act)

        try:
            count['serve_ratio'] = count['serves_made'] / count['serve_total']
        except ArithmeticError:
            count['serve_ratio'] = 0.0

        try:
            count['spike_ratio'] = (count['spikes_returned'] /
                                    count['spike_total'])
        except ArithmeticError:
            count['spike_ratio'] = 0.0

        count['missed_total'] = count['missed_sets'] + count['missed_spikes']

        return count

    @classmethod
    @abstractmethod
    def calculate(cls, game, precision=4):
        """Perform the stat calculations and register player stat."""
        return {'p1': None, 'p2': None, 'p3': None, 'p4': None}

    @classmethod
    def to_json(cls):
        """Encode the object into valid JSON."""
        return {'UID': None, 'name': cls.__name__}

    @classmethod
    def from_json(cls, data):
        """Decode the object from valid JSON."""
        model = None
        if util.has_keys(data, 'UID', 'name', error=JSONKeyError):
            model = StatModel.__stat_model_registry.get(data['name'])
            if model is None:
                raise NameError("Model not found.", data['name'])

        return model


class Model1(StatModel):
    """Current Model as of 6/25/17."""

    @classmethod
    def calculate(cls, game, precision=4):
        """Perform the stat calculations and register player stat."""
        stats = defaultdict(type(None))

        length = len(game)
        game_length_weight = 1 if length <= 39 else 39.0 / length

        for player in game.players.values():
            touchcomp = cls.touch_components(game, player)

            hitting = 20 * (1 - touchcomp['spike_ratio'])

            defense = (touchcomp['d_touch_nr'] + 0.4 * hitting *
                       touchcomp['d_touch_r']) * game_length_weight

            serving = 5.5 * touchcomp['aces'] + 15 * touchcomp['serve_ratio']

            cleanliness = (20 - 5 * touchcomp['missed_total'] - 2 * (
                touchcomp['tough_touch'] + touchcomp['aced']))

            stats[player] = {
                'hitting': round(hitting, precision),
                'defense': round(defense, precision),
                'serving': round(serving, precision),
                'cleanliness': round(cleanliness, precision),
                'total': round(hitting + defense + serving + cleanliness,
                               precision)
            }

        return stats


class DefaultStatModel(Model1):
    """The Current Default StatModel."""
