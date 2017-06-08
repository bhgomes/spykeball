"""Touch Classes."""

from abc import ABCMeta, abstractmethod

# maybe do type annotations
from spykeball.player import Player


class _AbstractTouch(metaclass=ABCMeta):
    """Abstract definition of a Spikeball touch."""

    def __init__(self, actor, success=True, target=None):
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

    def __init__(self, actor, success=True, target=None, is_ace=False):
        """Initialize Service."""
        self._is_ace = is_ace if success else False
        super().__init__(actor, success, target)

    @property
    def is_ace(self):
        """Determine if the serve is an ace."""
        return self._is_ace


class Set(_AbstractTouch):
    """Set."""

    def __init__(self, actor, success=True, strength=None):
        # none means it has no qualifier
        """Initialize Set."""
        self._strength = strength
        super().__init__(actor, success, target=None)

    @property
    def strength(self):
        """Return strength of Set."""
        return self._strength


class Spike(_AbstractTouch):
    """Spike."""

    def __init__(self, actor, success=True, strength=None):
        """Initialize Spike."""
        self._strength = strength
        super().__init__(actor, success, target=None)


class _AbstractReturn(_AbstractTouch):
    """Abstract Return."""

    def __init__(self, actor, success=True, strength=None):
        """Initialize Abstract Return."""
        self._strength = strength
        super().__init__(actor, success, target=None)

    @property
    def strength(self):
        """Return strength of Abstract Return."""
        return self._strength


class ServiceReturn(_AbstractReturn):
    """Service Return."""

    def __init__(self, actor, success=True, strength=None):
        """Initialize Service Return."""
        super().__init__(actor, success, strength)


class DefensiveReturn(_AbstractReturn):
    """Defensive Return."""

    def __init__(self, actor, success=True, strength=None):
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
        # add meta data like the score and stuff

        for point in actions:
            current_point = []
            current_step = 0
            service = True
            
            current_team = ("1", "2")
            other_team = ("3", "4")
            current_player = None
            
            action_deque = deque(point)
            
            next_obj = lambda: action_deque.popleft()
            
            def verify_action_deque_empty(error_on=False):
                if error_on:
                    if len(action_deque) == 0:
                        raise Exception("FIX THIS")
                else:
                    if len(action_deque) != 0:
                        raise Exception("FIX THIS")
            
            def swap_teams():
                if current_player not in current_team:
                    if current_player not in other_team:
                        raise Exception("FIX THIS")
                    else:
                        current_team, other_team = other_team, current_team
            
            while len(action_deque) != 0:
                if service:
                    current_player = next_obj()
                    
                    # swap teams if necessary
                    swap_teams()
                    
                    modifier = next_obj()
                    if modifier == "a":
                        target = next_obj()
                        current_point.append(Service(current, success=True, target=target, is_ace=True))
                        verify_action_deque_empty(error_on=False)
                    elif modifier in other_team:
                        current_point.append(Service(current, success=True, target=modifier))
                        current_player = modifier
                    elif modifier == "n":
                        current_point.append(Service(current, success=False))
                        verify_action_deque_empty(error_on=False)
                    else:
                        raise Exception("FIX THIS")
                    service = False
                else:
                    pass
            
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
