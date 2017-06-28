"""Touch Classes."""

__all__ = ['TouchException', 'Touch', 'Service', 'Defense', 'Set', 'Spike',
           'ErrorTouch', 'TOUCHMAP_LEXICON', 'TouchMapException',
           'parse_point', 'parse', 'TouchMapVerify', 'valid_touchmap',
           'valid_touchlist', 'load']

from collections import deque, namedtuple
from copy import deepcopy
from enum import Enum
from pathlib import Path

from . import io
from . import util

from .io import JSONKeyError

from .player import PlayerException
from .player import Player


class TouchException(Exception):
    """Raise an exception about a touch."""


class Touch(io.JSONSerializable):
    """Abstract definition of a Spikeball touch."""

    _next = None

    def __init__(self, actor, success=True, target=None, strength=None,
                 error=None):
        """Initialize Abstract Touch Class."""
        self._actor = actor
        self._success = success
        self._target = target
        self._strength = strength
        self._error = error

    def __str__(self):
        """String representation of the Touch Object."""
        success = ""
        if self._success:
            if self._strength == "s":
                success = "strong"
            elif self._strength == "w":
                success = "weak"
        else:
            success = "unsuccessful"

        return "{}({} {}{}{})".format(
            self.__class__.__name__,
            self._actor,
            success,
            "" if self._target is None else " to " + str(self._target),
            "" if self._error is None else " " + self._error.message)

    def to_json(self):
        """Encode the object into valid JSON."""
        touch = deepcopy(self.__dict__)
        for k, v in list(touch.items()):
            if k[0] == '_':
                touch[k[1:]] = touch.pop(k)
            if k[1:] == 'success' and v:
                touch.pop(k[1:])
            elif k[1:] in ('is_ace', 'strength', 'target', 'error') and not v:
                touch.pop(k[1:])
        touch['touch'] = self.__class__.__name__
        return touch

    @classmethod
    def from_json(cls, data):
        """Decode the object from valid JSON."""
        if util.has_keys(data, 'touch', 'actor', error=JSONKeyError):
            touch_type = data['touch']
            clz = None
            if touch_type == "Service":
                clz = Service
            elif touch_type == "Defense":
                clz = Defense
            elif touch_type == "Set":
                clz = Set
            elif touch_type == "Spike":
                clz = Spike
            else:
                raise ValueError("Touch attribute is invalid. Should be "
                                 "'Service', 'Defense', 'Set', or 'Spike'.",
                                 touch_type)

            return clz(data['actor'],
                       data.get('success', default=True),
                       data.get('target'),
                       data.get('strength'),
                       data.get('error')
                       )

    @property
    def actor(self):
        """Return actor Player."""
        return self._actor

    @actor.setter
    def actor(self, other):
        """Set actor Player."""
        self._actor = other

    @property
    def success(self):
        """Return success value."""
        return self._success

    @success.setter
    def success(self, other):
        """Set success value."""
        self._success = other

    @property
    def target(self):
        """Return target Player."""
        return self._target

    @target.setter
    def target(self, other):
        """Set target Player."""
        self._target = other

    @property
    def strength(self):
        """Return strength value."""
        return self._strength

    @strength.setter
    def strength(self, other):
        """Set strength value."""
        self._strength = other

    @property
    def error(self):
        """Return error value."""
        return self._error

    @error.setter
    def error(self, other):
        """Set error value."""
        self._error = other


class Service(Touch):
    """Service."""

    def __init__(self, actor, success=True, target=None, strength=None,
                 is_ace=False, error=None):
        """Initialize Service."""
        self._is_ace = is_ace if success else False
        super().__init__(actor, success, target, strength, error)

    def __str__(self):
        """String representation of the Touch Object."""
        success = ""
        if self._success:
            if self._strength == "s":
                success = "strong"
            elif self._strength == "w":
                success = "weak"
        else:
            success = "unsuccessful"

        return "{}({} {}{}{})".format(
            "Ace" if self._is_ace else "Service",
            self._actor,
            success,
            "" if self._target is None else " to " + str(self._target),
            "" if self._error is None else " " + self._error.message)

    @property
    def is_ace(self):
        """Determine if the serve is an ace."""
        return self._is_ace

    @is_ace.setter
    def is_ace(self, other):
        """Set ace value."""
        self._is_ace = other


class Defense(Touch):
    """Defensive Return."""


class Set(Touch):
    """Set."""


class Spike(Touch):
    """Spike."""

    def __str__(self):
        """String representation of the Spike Object."""
        success = ""
        if self._success:
            if self._strength == "s":
                success = "strong"
            elif self._strength == "w":
                success = "weak"
        else:
            success = "unsuccessful"

        return "{}({} {}{}{})".format(
            self.__class__.__name__,
            self._actor,
            success,
            "" if self._target is None else " on " + str(self._target),
            "" if self._error is None else " " + self._error.message)


Service._next = Defense
Defense._next = Set
Set._next = Spike
Spike._next = Defense


class ErrorTouch(Enum):
    """Describes erroneous touch types."""

    FutureMistake = ("causes loss of point")
    DoubleTouch = ("double touched")

    def __init__(self, message):
        """Initialize ErrorTouch with an error message."""
        self.message = message


TOUCHMAP_LEXICON = '1234aefnpsw'


class TouchMapException(Exception):
    """Raise an exception about a touch map."""


def parse_point(point, playermap):
    """Parse an action."""
    util.typecheck(point, str)
    util.typecheck(playermap, dict)
    util.haskeys(playermap, 'p1', 'p2', 'p3', 'p4', error=KeyError)
    util.isinnertype(playermap.values(), Player, error=TypeError)

    def pmap(pindex):
        valid_player = playermap.get('p' + pindex)
        if valid_player is None:
            raise PlayerException("Player is not part of this player list.",
                                  pindex, playermap.values())
        else:
            return valid_player

    touches = []
    touch = Service

    focus = None
    same_team = '12'
    other_team = '34'

    action_deque = deque(point)

    def next_touch():
        return action_deque.popleft()

    def is_deque_empty(error_on=False):
        if error_on and not action_deque:
            raise TouchMapException("No ending character.", point)
        elif action_deque:
            raise TouchMapException("Touch past end of play.", point)

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
                                        point, focus, same_team, other_team)

    while len(action_deque) != 0:
        if touch is Service:
            set_focus(next_touch())
            modifier = next_touch()

            if modifier == 'n':
                touches.append(Service(pmap(focus), success=False))
                is_deque_empty(error_on=False)
            elif modifier == 'a':
                target = next_touch()
                if target in other_team:
                    touches.append(Service(pmap(focus),
                                           target=pmap(target),
                                           is_ace=True))
                else:
                    raise TouchMapException("Player cannot ace a teammate.",
                                            point)
                is_deque_empty(error_on=False)
            elif modifier in other_team:
                touches.append(Service(pmap(focus), target=pmap(modifier)))
                set_focus(modifier)
                touch = Defense
            else:
                raise TouchMapException("Invalid character.", point)

        else:
            modifier = next_touch()

            if modifier in 'np':
                if modifier == 'n':
                    clz = Defense if touch is Defense else Spike
                    success = False
                else:
                    clz = Spike
                    success = True

                # how to determine if touch was a spike or a missed set

                touches.append(clz(pmap(focus), success=success))
                is_deque_empty(error_on=False)

            else:
                strength, error = None, None
                target = modifier

                if modifier in 'sw':
                    strength = modifier
                    target = next_touch()
                elif modifier == 'e':
                    target = next_touch()
                    if target in same_team:
                        error = ErrorTouch.FutureMistake
                    else:
                        raise TouchMapException("Invalid character.", point)

                if target in same_team or target in other_team:
                    if target in same_team and touch is Spike:
                        if target == focus:
                            error = ErrorTouch.DoubleTouch
                        else:
                            raise TouchMapException(
                                "Player cannot spike a teammate.", point)

                    if target in other_team:
                        touch = Spike

                    touches.append(touch(pmap(focus),
                                         target=pmap(target),
                                         strength=strength,
                                         error=error))
                    set_focus(target)
                    touch = touch._next

                else:
                    raise TouchMapException("Invalid character.", point)

    return touches


def parse(actions, playermap):
    """Parse strings of actions into Touches."""
    return [parse_point(point, playermap) for point in actions]


TouchMapVerify = namedtuple('TouchMapVerify', ['valid', 'inject'])


def valid_touchmap(point):
    """Return true if the point can be parsed and a valid parsing."""
    touchmap = None
    playermap = {
        'p1': Player('p1'),
        'p2': Player('p2'),
        'p3': Player('p3'),
        'p4': Player('p4')
    }
    try:
        touchmap = parse_point(point, playermap)
    except Exception:
        touchmap = None

    def inject(tm, playermap):
        for action in tm:
            if action.actor.name == 'p1':
                action.actor = playermap['p1']
            elif action.actor.name == 'p2':
                action.actor = playermap['p2']
            elif action.actor.name == 'p3':
                action.actor = playermap['p3']
            elif action.actor.name == 'p4':
                action.actor = playermap['p4']

            if action.target.name == 'p1':
                action.target = playermap['p1']
            elif action.target.name == 'p2':
                action.target = playermap['p2']
            elif action.target.name == 'p3':
                action.target = playermap['p3']
            elif action.target.name == 'p4':
                action.target = playermap['p4']

    if touchmap is None:
        return TouchMapVerify(False, lambda: None)
    else:
        return TouchMapVerify(True, lambda pmap: inject(touchmap, pmap))


def valid_touchlist(actions):
    """Return true if the actions can be parsed into valid points."""
    touches = (valid_touchmap(action) for action in actions)
    if all(touchmap.valid for touchmap in touches):
        return TouchMapVerify(True, lambda pmap: map(
            lambda act: act.inject(pmap), touches))
    else:
        return TouchMapVerify(False, lambda: None)


def load(fp, *delimeters):
    """Retrieve the touchmaps from a file."""
    if Path(fp).is_file:
        with open(fp, "r+") as file:
            return [s for s in io.readsplitby(file, ",", "\n", *delimeters)
                    if s != '']
