"""Touch Classes."""

__all__ = ['TouchException', 'Touch', 'Service', 'Defense', 'Set', 'Spike',
           'ErrorTouch', 'TOUCH_LEXICON', 'Rally', 'RallyException',
           'rally_parse', 'parse', 'rally_validate', 'validate',
           'rally_inject', 'inject', 'rally_select_actor',
           'rally_select_target', 'rally_select', 'select', 'load']

from collections import deque, namedtuple
from copy import deepcopy
from enum import Enum
from pathlib import Path

from . import io
from . import util

from .io import JSONKeyError
from .player import PlayerException

from .player import Player, PlayerMap


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


TOUCH_LEXICON = '1234aefnpsw'


Rally = namedtuple('Rally', ['playermap', 'touches'])


class RallyException(Exception):
    """Raise an exception about a rally."""


def rally_parse(rally, playermap):
    """Parse an action."""

    def pmap(pindex):
        valid_player = playermap[int(pindex) - 1]
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

    action_deque = deque(rally)

    def next_touch():
        return action_deque.popleft()

    def is_deque_empty(error_on=False):
        if error_on and not action_deque:
            raise RallyException("No ending character.", rally)
        elif action_deque:
            raise RallyException("Touch past end of play.", rally)

    def set_focus(player):
        nonlocal focus
        nonlocal same_team
        nonlocal other_team

        focus = player

        if focus not in same_team:
            if focus in other_team:
                same_team, other_team = other_team, same_team
            else:
                raise RallyException("Team collision.",
                                     rally, focus, same_team, other_team)

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
                    raise RallyException("Player cannot ace a teammate.",
                                         rally)
                is_deque_empty(error_on=False)
            elif modifier in other_team:
                touches.append(Service(pmap(focus), target=pmap(modifier)))
                set_focus(modifier)
                touch = Defense
            else:
                raise RallyException("Invalid character.", rally)

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
                        raise RallyException("Invalid character.", rally)

                if target in same_team or target in other_team:
                    if target in same_team and touch is Spike:
                        if target == focus:
                            error = ErrorTouch.DoubleTouch
                        else:
                            raise RallyException(
                                "Player cannot spike a teammate.", rally)

                    if target in other_team:
                        touch = Spike

                    touches.append(touch(pmap(focus),
                                         target=pmap(target),
                                         strength=strength,
                                         error=error))
                    set_focus(target)
                    touch = touch._next

                else:
                    raise RallyException("Invalid character.", rally)

    return Rally(playermap, touches)


def parse(rallies, playermap):
    """Parse strings of rallies into their constituant Touches."""
    for rally in rallies:
        yield rally_parse(rally, playermap)


def rally_validate(rally):
    """Return the rally if it can be parsed, else return an empty rally."""
    parsed_rally = None
    playermap = PlayerMap(
        Player('p1'),
        Player('p2'),
        Player('p3'),
        Player('p4')
    )

    try:
        parsed_rally = rally_parse(rally, playermap)
    except Exception:
        parsed_rally = None

    return Rally(playermap, parsed_rally)


def validate(rallies):
    """Validate the set of rallies."""
    for rally in rallies:
        yield rally_validate(rally)


def rally_inject(rally, playermap):
    """Replace the players of the rally with those in the playermap."""
    if rally.playermap != playermap:
        for touch in rally.touches:
            if touch.actor.UID == rally.playermap.p1.UID:
                touch.actor = playermap.p1
            elif touch.actor.UID == rally.playermap.p2.UID:
                touch.actor = playermap.p2
            elif touch.actor.UID == rally.playermap.p3.UID:
                touch.actor = playermap.p3
            elif touch.actor.UID == rally.playermap.p4.UID:
                touch.actor = playermap.p4

            if touch.target.UID == rally.playermap.p1.UID:
                touch.target = playermap.p1
            elif touch.target.UID == rally.playermap.p2.UID:
                touch.target = playermap.p2
            elif touch.target.UID == rally.playermap.p3.UID:
                touch.target = playermap.p3
            elif touch.target.UID == rally.playermap.p4.UID:
                touch.target = playermap.p4
    return rally


def inject(rallies, playermap):
    """Replace the players of the rally with those in the playermap."""
    for rally in rallies:
        yield rally_inject(rally, playermap)


def rally_select_actor(rally, player):
    """Select touches which the player is an actor."""
    for touch in rally.touches:
        if touch.actor == player:
            yield touch


def rally_select_target(rally, player):
    """Select touches which the player is an target."""
    for touch in rally.touches:
        if touch.target == player:
            yield touch


def rally_select(rally, player):
    """Select touches which the player is involved in."""
    yield from rally_select_actor(rally, player)
    yield from rally_select_target(rally, player)


def select(rallies, player):
    """Select rallies which the player is involved in."""
    for rally in rallies:
        yield from rally_select(rally, player)


def load(fp, *delimeters):
    """Retrieve the rallies from a file."""
    if Path(fp).is_file:
        with open(fp, "r+") as file:
            rallies = [s for s in io.readsplitby(file, ",", "\n", *delimeters)
                       if s != '']
            yield from validate(rallies)
