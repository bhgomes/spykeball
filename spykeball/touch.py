"""Touch Classes."""

from copy import deepcopy
from collections import deque

from spykeball.core import io
from spykeball.core import util
from spykeball.core.exception import (
    PlayerException,
    TouchMapException,
    JSONKeyError,
)
from spykeball.player import Player


class _AbstractTouch(io.JSONSerializable):
    """Abstract definition of a Spikeball touch."""

    _next = None

    def __init__(self, actor, success=True, target=None, strength=None):
        """Initialize Abstract Touch Class."""
        self._actor = actor
        self._success = success
        self._target = target
        self._strength = strength

    def __str__(self):
        """String representation of the Touch Object."""
        success = "unsuccessful"
        if self._success:
            if self._strength == "s":
                success = "strong"
            elif self._strength == "w":
                success = "weak"

        return "{}({} {}{})".format(
            self.__class__.__name__,
            self._actor,
            success,
            ("" if self._target is None else " to " + str(self._target)))

    def to_json(self):
        """Encode the object into valid JSON."""
        out = deepcopy(self.__dict__)
        for k, v in list(out.items()):
            if k[0] == '_':
                out[k[1:]] = out.pop(k)

            if k[1:] == 'success' and v:
                out.pop(k[1:])
            elif k[1:] in ('is_ace', 'strength', 'target') and not v:
                out.pop(k[1:])
        out['touch'] = self.__class__.__name__
        return out

    @classmethod
    def from_json(cls, data):
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
        super().__init__(actor, success, target, strength)

    def __str__(self):
        """String representation of the Touch Object."""
        success = "unsuccessful"
        if self._success:
            if self._strength == "s":
                success = "strong"
            elif self._strength == "w":
                success = "weak"

        return "{}({} {}{})".format(
            "Ace" if self._is_ace else "Service",
            self._actor,
            success,
            ("" if self._target is None else " to " + str(self._target)))

    @property
    def is_ace(self):
        """Determine if the serve is an ace."""
        return self._is_ace


class Defense(_AbstractTouch):
    """Defensive Return."""


class Set(_AbstractTouch):
    """Set."""


class Spike(_AbstractTouch):
    """Spike."""

    def __str__(self):
        """String representation of the Spike Object."""
        success = "unsuccessful"
        if self._success:
            if self._strength == "s":
                success = "strong"
            elif self._strength == "w":
                success = "weak"

        return "{}({} {}{})".format(
            self.__class__.__name__,
            self._actor,
            success,
            ("" if self._target is None else " on " + str(self._target)))


Service._next = Defense
Defense._next = Set
Set._next = Spike
Spike._next = Defense


class ActionList(util.PlayerInterface, io.JSONSerializable):
    """List of actions."""

    def __init__(self, p1, p2, p3, p4, *actions):
        """Instantiate an ActionList."""
        super().__init__(p1, p2, p3, p4)
        self._action_strings = list(actions)

        if p1 and p2 and p3 and p4:
            self._actionlist = ActionList.parse(p1, p2, p3, p4, *actions)
            self._parsed = True
        else:
            self._actionlist = None
            self._parsed = False

        self._outer_index = 0
        self._inner_index = 0

    def __str__(self):
        """Return string representation of the ActionList."""
        out = "ActionList({\n\n"
        if self._parsed:
            for i, a in enumerate(self._actionlist):
                out += "  " + self._action_strings[i] + ":\n"
                for b in a:
                    out += "    " + str(b) + "\n"
                out += "\n"
        else:
            for e in self._action_strings:
                out += "  " + e + "\n"
        return out + "})"

    def __getitem__(self, index):
        """Get item from ActionList."""
        if isinstance(index, int):
            return self._actionlist[index]
        elif isinstance(index, Player):
            return self._get_actions_from(index)
        else:
            return None

    def __setitem__(self, key, item):
        """Set item from ActionList."""
        if isinstance(item, str):
            self._action_strings[key] = item
            if self._parsed:
                self._actionlist[key] = ActionList.parse(
                    self._p1, self._p2, self._p3, self._p4, *(item))[0]
        else:
            raise TypeError("Not a valid key.", key, type(key))

    def __iter__(self):
        """Return iterator object for ActionList."""
        return self

    def __next__(self):
        """Return next action in the ActionList."""
        if self._parsed:
            if self._outer_index >= len(self._actionlist):
                raise StopIteration
            else:
                out = self._actionlist[self._outer_index][self._inner_index]
                self._inner_index += 1
                if (self._inner_index >=
                        len(self._actionlist[self._outer_index])):
                    self._inner_index = 0
                    self._outer_index += 1
                return out
        else:
            if self._outer_index >= len(self._action_strings):
                raise StopIteration
            else:
                out = self._action_strings[self._outer_index]
                self._outer_index += 1
                return out

    def __contains__(self, item):
        """Return True if item is contained in ActionList."""
        if self._parsed:
            return (
                item in self._action_strings or
                item in self._actionlist or
                any(item in m for m in self._actionlist))
        else:
            return item in self._action_strings

    def __len__(self):
        """Return length of ActionList."""
        if self._parsed:
            return len(self._actionlist)
        else:
            return len(self._action_strings)

    def _get_actions_from(self, player):
        """Find all actions related to the player and return."""
        if not self._parsed:
            raise PlayerException("No players registered.", None)

        output = {"actor": [], "target": []}

        for play in self._actionlist:
            for action in play:
                if action.actor == player:
                    output["actor"].append(action)

                if action.target == player:
                    output["target"].append(action)

        return output

    def subaction_groups(self):
        """Return subactions that represent each point of the ActionList."""
        if not self._parsed:
            raise PlayerException("No players registered.", None)

        group = 0
        while group < len(self._actionlist):
            yield self._actionlist[group]
            group += 1

    @classmethod
    def from_strings(cls, *actions):
        """Create a list based only on string based inputs."""
        return cls(None, None, None, None, *actions)

    @property
    def actions(self):
        """Return actions as AbstractTouches."""
        return self._actionlist if self._parsed else self._action_strings

    @actions.setter
    def actions(self, *acts):
        """Set the actions."""
        self._action_strings = acts
        if self._parsed:
            self._actionlist = ActionList.parse(
                self._p1, self._p2, self._p3, self._p4, *acts)

    @property
    def as_strings(self):
        """Return the ActionList as a list of strings."""
        return self._action_strings

    @property
    def parsed(self):
        """Return true if ActionList has been parsed."""
        return self._parsed

    @staticmethod
    def parse(p1, p2, p3, p4, *actions):
        """Parse actions into AbstractTouches."""
        output = []

        def pmap(player):
            out = {"1": p1, "2": p2, "3": p3, "4": p4}.get(player)
            if out is None:
                raise PlayerException(
                    "Player is not part of this player list.",
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
                        raise TouchMapException("No ending character.", point)
                else:
                    if len(action_deque) != 0:
                        raise TouchMapException(
                            "Touch past end of play.", point)

            def set_focus(player):
                nonlocal focus
                nonlocal same_team
                nonlocal other_team

                focus = player

                if focus not in same_team:
                    if focus in other_team:
                        same_team, other_team = other_team, same_team
                    else:
                        raise TouchMapException("Team collision.",
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
                            raise TouchMapException(
                                "Player cannot ace a teammate", point)
                        verify_action_deque_empty(error_on=False)
                    elif modifier in other_team:
                        touches.append(Service(pmap(focus),
                                               target=pmap(modifier)))
                        set_focus(modifier)
                        touch = Defense
                    else:
                        raise TouchMapException("Invalid character.", point)

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
                                raise TouchMapException(
                                    "Player cannot spike on a teammate", point)

                            if target in other_team:
                                touch = Spike

                            touches.append(touch(pmap(focus),
                                                 target=pmap(target),
                                                 strength=strength))
                            set_focus(target)
                            touch = touch._next

                        else:
                            raise TouchMapException(
                                "Invalid character.", point)

            output.append(touches)

        return output

    def to_json(self, with_touches=True):
        """Encode the object into valid JSON."""
        actionlist = {
            "class": "ActionList",
            "strings": self._action_strings
        }

        if with_touches and self._parsed:
            actionlist['players'] = {
                'p1': self._p1,
                'p2': self._p2,
                'p3': self._p3,
                'p4': self._p4
            }

            actionlist['touches'] = self._actionlist

        return actionlist

    @classmethod
    def from_json(cls, data, with_touches=True):
        """Decode the object from valid JSON."""
        actionlist = None
        if util.has_keys(data, 'class', 'strings'):
            if with_touches:
                if (util.has_keys(data, 'players', 'touches') and
                        util.has_keys(data['players'],
                                      'p1', 'p2', 'p3', 'p4')):
                    p1 = Player.from_json(data['players']['p1'])
                    p2 = Player.from_json(data['players']['p2'])
                    p3 = Player.from_json(data['players']['p3'])
                    p4 = Player.from_json(data['players']['p4'])
                    actionlist = cls(p1, p2, p3, p4, data['strings'])
                else:
                    raise JSONKeyError(data, ('players', 'touches'))
            else:
                actionlist = cls.from_strings(data['strings'])
        else:
            raise JSONKeyError(data, 'class', 'strings')

        return actionlist

    def save(self, fp, with_touches=True):
        """Save ActionList contents to a JSON file."""
        super().save(fp, with_touches and self._parsed)

    @classmethod
    def load(cls, fp, with_touches=True):
        """Load ActionList contents from a JSON file."""
        if io.ext_matches(fp, '.txt'):
            with open(fp, 'r+') as file:
                return cls.from_strings(*filter(lambda x: x != '',
                                                io.readsplit(file, ',', '\n')))
        else:
            return super().load(fp, with_touches)
