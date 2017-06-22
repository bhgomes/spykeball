"""Statistics Module."""

from abc import ABCMeta, abstractmethod

from spykeball import io
from spykeball import util

from spykeball import PlayerException
from spykeball import TouchException

from spykeball import Defense
from spykeball import Set
from spykeball import Spike
from spykeball import Service


class StatModel(io.JSONSerializable, metaclass=ABCMeta):
    """Interpret a game."""

    __stat_model_registry = {}

    def __new__(cls, name, bases, attr):
        """Add class to the StatModel registry after creation."""
        model = StatModel.__stat_model_registry.get(name)
        if model is None:
            StatModel.__stat_model_registry[name] = cls
        else:
            raise NameError("No two StatModels can have the same name.", name)
        return super().__new__(name, bases, attr)

    @staticmethod
    def touch_components(action_list, player):
        """Return the relevant touch_components for each player."""
        actions = action_list[player]

        if actions is None:
            raise PlayerException("Player is not part of the ActionList.",
                                  player,
                                  action_list)

        performed = actions.get("actor")
        recieved = actions.get("target")

        components = ['aces', 'aced', 'serves_made', 'serve_total',
                      'serve_ratio', 'spikes_returned', 'spike_total',
                      'spike_ratio', 'd_touch_r', 'd_touch_nr', 'missed_sets',
                      'missed_spikes', 'missed_total', 'tough_touch'
                      ]

        count = dict(zip(components, [0] * len(components)))

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
                raise TouchException(
                    "Action must be of subtype _AbstractTouch", act)

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
                raise TouchException(
                    "Action must be of subtype _AbstractTouch", act)

        count['serve_ratio'] = count['serves_made'] / count['serve_total']
        count['spike_ratio'] = count['spikes_returned'] / count['spike_total']
        count['missed_total'] = count['missed_sets'] + count['missed_spikes']

        return count

    @staticmethod
    @abstractmethod
    def calculate(action_list, precision=4):
        """Perform the stat calculations and register player stat."""
        return {"p1": None, "p2": None, "p3": None, "p4": None}

    @classmethod
    def to_json(cls):
        """Encode the object into valid JSON."""
        return {"UID": None, "name": cls.__name__}

    @classmethod
    def from_json(cls, data):
        """Decode the object from valid JSON."""
        model = None
        if util.has_keys(data, 'UID', 'name'):
            model = StatModel.__stat_model_registry.get(data['name'])
            if model is None:
                raise NameError("Model not found.", data['name'])

        return model


class Model1(StatModel):
    """Current Model as of 6/20/17."""

    def calculate(action_list, precision=4):
        """Perform the stat calculations and register player stat."""
        stats = {
            action_list.p1: None,
            action_list.p2: None,
            action_list.p3: None,
            action_list.p4: None
        }

        length = len(action_list)

        game_length_weight = 1 if length <= 39 else 39.0 / length

        for player in stats.keys():
            components = Model1.touch_components(action_list, player)

            try:
                hitting = 20 * (1 - components['spike_ratio'])
            except ArithmeticError:
                hitting = 0.0

            try:
                defense = (components['d_touch_nr'] + 0.4 * hitting *
                           components['d_touch_r']) * game_length_weight
            except ArithmeticError:
                defense = 0.0

            try:
                serving = (5.5 * components['aces'] + 15 *
                           components['serve_ratio'])
            except ArithmeticError:
                serving = 0.0

            try:
                cleanliness = (20 - 5 * components['missed_total'] - 2 * (
                    components['tough_touch'] + components['aced']))
            except ArithmeticError:
                cleanliness = 0.0

            stats[player] = {
                "hitting": round(hitting, precision),
                "defense": round(defense, precision),
                "serving": round(serving, precision),
                "cleanliness": round(cleanliness, precision),
                "total": round(hitting + defense + serving + cleanliness,
                               precision)
            }

        return stats


class DefaultStatModel(Model1):
    """The Default Stat Model."""


class StatModelRegister(object):
    """Return a StatModel from the Name."""
