"""Touch Classes."""

from collections import deque

from spykeball.core import util
from spykeball.core.exception import (
    InvalidPlayerException,
    InvalidTouchMapException
)
from spykeball.player import Player


class _AbstractTouch(util.JSONSerializable):
    """Abstract definition of a Spikeball touch."""

    next = None

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Abstract Touch Class."""
        self._actor = actor
        self._success = success
        self._target = target
        self._strength = strength

    def __str__(self):
        """String representation of the Touch Object."""
        actor = str(self._actor)

        success = ""

        if self._success:
            if self._strength == "s":
                success = " strong"
            elif self._strength == "w":
                success = " weak"
        else:
            success = " unsuccessful"

        target = "" if self._target is None else " to " + str(self._target)
        return self.__class__.__name__ + "(" + actor + success + target + ")"

    def to_json(self):
        """Encode the object into valid JSON."""
        out = self.__dict__
        out['class'] = self.__class__
        return out

    def from_json(self, s):
        """Decode the object from valid JSON."""
        return None

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
        return self._target

    @property
    def strength(self):
        """Return strength of the Touch."""
        return self._strength


class Service(_AbstractTouch):
    """Service."""

    def __init__(self, actor, success=True, target=None, strength=None,
                 is_ace=False):
        """Initialize Service."""
        self._is_ace = is_ace if success else False
        super().__init__(actor, success, target)

    def __str__(self):
        """String representation of the Touch Object."""
        actor = str(self._actor)

        success = ""

        if self._success:
            if self._strength == "s":
                success = " strong"
            elif self._strength == "w":
                success = " weak"
        else:
            success = " unsuccessful"

        target = "" if self._target is None else " on " + str(self._target)
        return ("Ace(" if self._is_ace else "Service(") + \
            actor + success + target + ")"

    def to_json(self):
        """Encode the object into valid JSON."""
        out = super().to_json()
        out['class'] = "Ace" if self._is_ace else "Service"
        return out

    def from_json(self, s):
        """Decode the object from valid JSON."""
        return None

    @property
    def is_ace(self):
        """Determine if the serve is an ace."""
        return self._is_ace


class Defense(_AbstractTouch):
    """Defensive Return."""

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Defensive Return."""
        super().__init__(actor, success, target, strength)

    def __str__(self):
        """String representation of the Defense Object."""
        return super().__str__()


class Set(_AbstractTouch):
    """Set."""

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Set."""
        super().__init__(actor, success, target, strength)

    def __str__(self):
        """String representation of the Set Object."""
        return super().__str__()


class Spike(_AbstractTouch):
    """Spike."""

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Spike."""
        super().__init__(actor, success, target, strength)

    def __str__(self):
        """String representation of the Spike Object."""
        actor = str(self._actor)

        success = ""

        if self._success:
            if self._strength == "s":
                success = " strong"
            elif self._strength == "w":
                success = " weak"
        else:
            success = " unsuccessful"

        target = "" if self._target is None else " on " + str(self._target)
        return self.__class__.__name__ + "(" + actor + success + target + ")"


Service.next = Defense
Defense.next = Set
Set.next = Spike
Spike.next = Defense


class ActionList(util.JSONSerializable):
    """List of actions."""

    def __init__(self, p1, p2, p3, p4, *actions):
        """Instantiate an ActionList."""
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._actionlist_strings = list(actions)
        self._actionlist = ActionList.parse(p1, p2, p3, p4, *actions)
        self._outer_index = 0
        self._inner_index = 0

    def __str__(self):
        """Return string representation of the ActionList."""
        out = "ActionList({\n\n"
        for i, a in enumerate(self._actionlist):
            out += "  " + self._actionlist_strings[i] + ":\n"
            for b in a:
                out += "    " + str(b) + "\n"
            out += "\n"
        return out + "})"

    def to_json(self):
        """Encode the object into valid JSON."""
        return {
            "class": "ActionList",
            "strings": self._actionlist_strings,
            "actions": self._actionlist
            }

    def from_json(self, s):
        """Decode the object from valid JSON."""
        return None

    def __getitem__(self, index):
        """Get item from ActionList."""
        if isinstance(index, int):
            return self._actionlist[index]
        elif isinstance(index, Player):
            return self._get_actions_from(index)
        else:
            return None

    def _get_actions_from(self, player):
        """Find all actions related to the player and return."""
        output = {"actor": [], "target": []}

        for play in self._actionlist:
            for action in play:
                if action.actor == player:
                    output["actor"].append(action)

                if action.target == player:
                    output["target"].append(action)

        return output

    def __setitem__(self, key, item):
        """Set item from ActionList."""
        if isinstance(item, str):
            self._actionlist_strings[key] = item
            self._actionlist[key] = ActionList.parse(
                self._p1, self._p2, self._p3, self._p4, item)[0]
        else:
            raise TypeError("Not a valid key.", key, type(key))

    def __iter__(self):
        """Return iterator object for ActionList."""
        return self

    def __next__(self):
        """Return next action in the ActionList."""
        if self._outer_index >= len(self._actionlist):
            raise StopIteration
        else:
            out = self._actionlist[self._outer_index][self._inner_index]
            self._inner_index += 1
            if self._inner_index >= len(self._actionlist[self._outer_index]):
                self._inner_index = 0
                self._outer_index += 1
            return out

    def __contains__(self, item):
        """Return True if item is contained in ActionList."""
        return item in self._actionlist or item in self._actionlist_strings

    def __len__(self):
        """Return length of ActionList."""
        return len(self._actionlist)

    @staticmethod
    def parse(p1, p2, p3, p4, *actions):
        """Parse actions into AbstractTouches."""
        output = []

        def pmap(player):
            out = {"1": p1, "2": p2, "3": p3, "4": p4}.get(player)
            if out is None:
                raise InvalidPlayerException(
                    "Player is not part of this player list",
                    player, (p1, p2, p3, p4))
            else:
                return out

        for point in actions:
            touches = []
            touch = Service

            focus = None
            same_team = ("1", "2")
            other_team = ("3", "4")

            action_deque = deque(point)

            def next_touch():
                return action_deque.popleft()

            def verify_action_deque_empty(error_on=False):
                if error_on:
                    if len(action_deque) == 0:
                        raise InvalidTouchMapException(
                            "No ending character.", point)
                else:
                    if len(action_deque) != 0:
                        raise InvalidTouchMapException(
                            "Characters past end of play.", point)

            def set_focus(player):
                nonlocal focus
                nonlocal same_team
                nonlocal other_team

                focus = player

                if focus not in same_team:
                    if focus in other_team:
                        same_team, other_team = other_team, same_team
                    else:
                        raise InvalidTouchMapException("Team collision.",
                                                       point,
                                                       focus,
                                                       same_team,
                                                       other_team)

            while len(action_deque) != 0:
                if touch is Service:
                    set_focus(next_touch())
                    modifier = next_touch()

                    if modifier == "n":
                        touches.append(Service(pmap(focus), success=False))
                        verify_action_deque_empty(error_on=False)
                    elif modifier == "a":
                        target = next_touch()
                        if target in other_team:
                            touches.append(Service(pmap(focus),
                                                   target=pmap(target),
                                                   is_ace=True))
                        else:
                            raise InvalidTouchMapException(
                                "Player cannot ace a teammate", point)
                        verify_action_deque_empty(error_on=False)
                    elif modifier in other_team:
                        touches.append(Service(pmap(focus),
                                               target=pmap(modifier)))
                        set_focus(modifier)
                        touch = Defense
                    else:
                        raise InvalidTouchMapException(
                            "Invalid character.", point)

                else:
                    modifier = next_touch()

                    if modifier in ("n", "p"):
                        if modifier == "n":
                            clz = Defense if touch is Defense else Spike
                            success = False
                        else:
                            clz = Spike
                            success = True

                        # how to determine if touch was a spike or a missed set

                        touches.append(clz(pmap(focus), success=success))
                        verify_action_deque_empty(error_on=False)

                    else:
                        strength = None
                        target = modifier

                        if modifier in ("s", "w"):
                            strength = modifier
                            target = next_touch()

                        if target in same_team or target in other_team:
                            if target in same_team and touch is Spike:
                                raise InvalidTouchMapException(
                                    "Player cannot spike on a teammate", point)

                            if target in other_team:
                                touch = Spike

                            touches.append(touch(pmap(focus),
                                                 target=pmap(target),
                                                 strength=strength))
                            set_focus(target)
                            touch = touch.next

                        else:
                            raise InvalidTouchMapException(
                                "Invalid character.", point)

            output.append(touches)

        return output

    @property
    def actions(self):
        """Return actions as AbstractTouches."""
        return self._actionlist

    @actions.setter
    def actions(self, *acts):
        """Set the actions."""
        self._actionlist_strings = acts
        self._actionlist = ActionList.parse(
            self._p1, self._p2, self._p3, self._p4, *acts)

    def subaction_groups(self):
        """Return Subaction that represent each point of the Game."""
        group = 0
        while group < len(self._actionlist):
            yield self._actionlist[group]
            group += 1

    @property
    def as_strings(self):
        """Return the ActionList as a list of strings."""
        return self._actionlist_strings

    @property
    def p1(self):
        """Return Player 1."""
        return self._p1

    @property
    def p2(self):
        """Return Player 2."""
        return self._p2

    @property
    def p3(self):
        """Return Player 3."""
        return self._p3

    @property
    def p4(self):
        """Return Player 4."""
        return self._p4
