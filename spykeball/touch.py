"""Touch Classes."""

from abc import ABCMeta, abstractmethod

# maybe do type annotations
from spykeball.player import Player


class _AbstractTouch(metaclass=ABCMeta):
    """Abstract definition of a Spikeball touch."""

    def __init__(self, actor, success, target):
        """Initialize Abstract Touch Class."""
        self._actor = actor
        self._success = success
        self._target = target

    @property
    def actor(self):
        """Return actor Player."""
        return self._actor

    @property
    def success(self):
        """True if the touch was successful for the actor."""
        return self._success

    @property
    def target(self):
        """Return target Player."""
        return self._player


class Service(_AbstractTouch):
    """Service."""

    def __init__(self, actor, success, target, is_ace):
        """Initialize Service."""
        self._is_ace = is_ace if success else False
        super().__init__(actor, success, target)

    @property
    def is_ace(self):
        """Determine if the serve is an ace."""
        return self._is_ace


class Set(_AbstractTouch):
    """Set."""

    def __init__(self, actor, success, strength):
        """Initialize Set."""
        self._strength = strength
        super().__init__(actor, success, target=None)

    @property
    def strength(self):
        """Return strength of Set."""
        return self._strength


class Spike(_AbstractTouch):
    """Spike."""

    def __init__(self, actor, success, strength):
        """Initialize Spike."""
        self._strength = strength
        super().__init__(actor, success, target=None)


class _AbstractReturn(_AbstractTouch):
    """Abstract Return."""

    def __init__(self, actor, success, strength):
        """Initialize Abstract Return."""
        self._strength = strength
        super().__init__(actor, success, target=None)

    @property
    def strength(self):
        """Return strength of Abstract Return."""
        return self._strength


class ServiceReturn(_AbstractReturn):
    """Service Return."""

    def __init__(self, actor, success, strength):
        """Initialize Service Return."""
        super().__init__(actor, success, strength)


class DefensiveReturn(_AbstractReturn):
    """Defensive Return."""

    def __init__(self, actor, success, strength):
        """Initialize Defensive Return."""
        super().__init__(actor, success, strength)


class ActionList(object):
    """List of actions."""

    def __init__(self, p1, p2, p3, p4, *actions):
        """Instantiate an ActionList."""
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._meta = {}
        self._action_list_strings = actions
        self._action_list = ActionList.parse(p1, p2, p3, p4, actions)

    def __str__(self):
        """Return string representation of the ActionList."""
        return ", ".join(self._action_list_strings)

    @staticmethod
    def parse(p1, p2, p3, p4, *actions):
        """Parse actions into AbstractTouches."""
        output = []

        for a, action in enumerate(actions):
            current_point = []
            current_step = 0
            current_team = 0
            current_player = None
            for s, step in enumerate(action):

                def assign_player(player, team_num):
                    global current_player
                    global current_team
                    current_player = player
                    current_team = team_num
                    return current_player

                action_type_dictionary = {
                    "1": assign_player(p1, 1),
                    "2": assign_player(p2, 1),
                    "3": assign_player(p3, 2),
                    "4": assign_player(p4, 2),
                    "a": None,
                    "e": None,
                    "n": None,
                    "p": None,
                    "s": None,
                    "w": None
                }

                value = action_type_dictionary.get(step)
                if value is None:
                    # add to this error
                    raise KeyError("Not a valid action-string", action)
                
            output.append(current_point)

        return output

    @property
    def actions(self):
        """Return actions as AbstractTouches."""
        return self._action_list

    @actions.setter
    def actions(self, *acts):
        """Set the actions."""
        self._action_list_strings = acts
        self._action_list = ActionList.parse(
            self._p1, self._p2, self._p3, self._p4, acts)

    @property
    def as_string_list(self):
        """Return the ActionList as a list of strings."""
        return self._action_list_strings

    @property
    def meta(self):
        """Return metadata on the game."""
        return self._meta

    def compile_actions(self, player):
        """Find all actions related to the player and return."""
        output = {"actor": [], "target": []}

        return output
