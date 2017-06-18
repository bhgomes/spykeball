"""Statistics Module."""

from abc import ABCMeta, abstractmethod

from spykeball.core import io
# from spykeball.core import util
from spykeball.core.exception import InvalidPlayerException
from spykeball.touch import Defense, Set, Spike, Service

# resolve metaclass conflict then add util.UIDClass


class StatModel(io.JSONSerializable, metaclass=ABCMeta):
    """Interpret a game."""

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
    def from_json(cls, s):
        """Decode the object from valid JSON."""


class Model1(StatModel):
    """Current Model as of 6/10/17."""

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
            actions = action_list[player]

            if actions is None:
                raise InvalidPlayerException(
                    "Player is not part of the ActionList.",
                    player,
                    action_list)

            performed = actions.get("actor")
            recieved = actions.get("target")

            aces = 0
            aced = 0
            serves_made = 0
            total_serves = 0
            spikes_returned = 0
            total_spikes = 0
            d_touch_r = 0
            d_touch_nr = 0
            missed_sets = 0
            missed_spikes = 0
            tough_touch = 0

            for act in performed:
                if isinstance(act, Service):
                    if act.success:
                        serves_made += 1
                        if act.is_ace:
                            aces += 1
                    total_serves += 1
                elif isinstance(act, Defense):
                    if act.success:
                        d_touch_r += 1
                    else:
                        d_touch_nr += 1

                    if act.strength == "w":
                        tough_touch += 1
                elif isinstance(act, Set):
                    if not act.success:
                        missed_sets += 1

                    if act.strength == "w":
                        tough_touch += 1
                elif isinstance(act, Spike):
                    if act.success:
                        spikes_returned += 1
                    else:
                        missed_spikes += 1
                    total_spikes += 1
                else:
                    raise TypeError(
                        "Action must be of subtype _AbstractTouch", act)

            for act in recieved:
                if isinstance(act, Service):
                    if act.is_ace:
                        aced += 1
                elif isinstance(act, Defense):
                    pass
                elif isinstance(act, Set):
                    pass
                elif isinstance(act, Spike):
                    pass
                else:
                    raise TypeError(
                        "Action must be of subtype _AbstractTouch", act)

            try:
                hitting = round(20 * (1 - spikes_returned / total_spikes),
                                precision)
            except ArithmeticError:
                hitting = 0.0

            try:
                defense = round((d_touch_nr + 0.4 * hitting * d_touch_r) *
                                game_length_weight, precision)
            except ArithmeticError:
                defense = 0.0

            try:
                serving = round(5.5 * aces + 15 * (serves_made / total_serves),
                                precision)
            except ArithmeticError:
                serving = 0.0

            try:
                cleanliness = round(20 - 5 * (missed_sets + missed_spikes) - 2
                                    * (tough_touch + aced), precision)
            except ArithmeticError:
                cleanliness = 0.0

            stats[player] = {
                "total": hitting + defense + serving + cleanliness,
                "hitting": hitting,
                "defense": defense,
                "serving": serving,
                "cleanliness": cleanliness
            }

        return stats


class DefaultStatModel(Model1):
    """The Default Stat Model."""


class StatModelRegister(object):
    """Return a StatModel from the Name."""
