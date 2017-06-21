"""Touch Classes."""

from copy import deepcopy
from enum import Enum

from spykeball.core import io
from spykeball.core import util
from spykeball.core.exception import (
    JSONKeyError,
)


class _AbstractTouch(io.JSONSerializable):
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
        touch = None
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

            touch = clz(data['actor'],
                        data.get('success', default=True),
                        data.get('target'),
                        data.get('strength'),
                        data.get('error')
                        )

        return touch

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


class Service(_AbstractTouch):
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


class Defense(_AbstractTouch):
    """Defensive Return."""


class Set(_AbstractTouch):
    """Set."""


class Spike(_AbstractTouch):
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


class TouchError(Enum):
    """Describes erroneous touch types."""

    FutureMistake = ("causes loss of point")
    DoubleTouch = ("double touched")

    def __init__(self, message):
        """Initialize TouchError with an error message."""
        self.message = message
