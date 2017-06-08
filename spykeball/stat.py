"""Statistics Module."""

from abc import ABCMeta, abstractmethod

from spykeball.core.exception import InvalidGameException
from spykeball.touch import Set, Spike, DefensiveReturn, Service


class StatModel(metaclass=ABCMeta):
    """Interpret a game."""

    @abstractmethod
    def __call__(self, action_list):
        """Perform the stat calculations and register player stat."""
        return {"p1": None, "p2": None, "p3": None, "p4": None}


class Model1(StatModel):
    """Current Model as of 6/7/17."""

    def __call__(self, action_list):
        """Perform the stat calculations and register player stat."""
        meta = action_list.meta
        p1 = meta.get("p1")
        p2 = meta.get("p2")
        p3 = meta.get("p3")
        p4 = meta.get("p4")
        stats = {p1: None, p2: None, p3: None, p4: None}

        length = meta.get("length")

        game_length_weight = 1 if length <= 39 else 39.0/length

        for player in stats.keys():
            actions = action_list.compile_actions(player)
            performed = actions.get("actor")
            recieved = actions.get("target")

            spikes_returned = 0
            total_spikes = 0
            d_touch_r = 0
            d_touch_nr = 0
            aces = 0
            aced = 0
            serves_made = 0
            total_serves = 0
            missed_sets = 0
            tough_touch = 0
            missed_spikes = 0

            for act in performed:
                if isinstance(act, Set):
                    pass
                elif isinstance(act, Spike):
                    pass
                elif isinstance(act, DefensiveReturn):
                    if act.successful:
                        d_touch_r += 1
                    else:
                        d_touch_nr += 1
                elif isinstance(act, Service):
                    if act.successful:
                        serves_made += 1
                        if act.is_ace:
                            aces += 1
                    total_serves += 1
                else:
                    pass

            for act in recieved:
                if isinstance(act, Service):
                    if act.is_ace:
                        aced += 1
                elif isinstance(act, Spike):
                    pass
                else:
                    pass

            hitting = 20 * (1 - spikes_returned/total_spikes)

            defense = (d_touch_nr + 0.4 * hitting * d_touch_r) * \
                game_length_weight

            serving = 5.5 * aces + 15 * (serves_made/total_serves)

            cleanliness = 20 - 5 * (missed_sets + missed_spikes) - \
                2 * (tough_touch + aced)

            stats[player] = {
                "total": hitting + defense + serving + cleanliness,
                "hitting": hitting,
                "defense": defense,
                "serving": serving,
                "cleanliness": cleanliness
            }

        return stats
