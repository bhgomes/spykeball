"""Touch Classes."""

from spykeball.player import Player


class _AbstractTouch(object):
    """Abstract definition of a Spikeball touch."""

    def __init__(self, actor: Player, target: Player):
        pass


class Service(_AbstractTouch):
    """Service."""

    pass


class Set(_AbstractTouch):
    """Set."""

    pass


class _AbstractReturn(_AbstractTouch):
    """Abstract Return."""

    pass


class ServiceReturn(_AbstractReturn):
    """Service Return."""

    pass


class DefensiveReturn(_AbstractReturn):
    """Defensive Return."""

    pass


class ActionList(object):
    """List of actions."""

    def __init__(self, *actions):
        """Instantiate an ActionList."""
        self.actions(actions)
        # self._action_list_strings = actions
        # self._action_list = ActionList.parse(actions)

    @staticmethod
    def parse(*actions):
        """Parse actions into AbstractTouches."""
        return None

    @property
    def actions(self):
        """Return actions as AbstractTouches."""
        return self._action_list

    @actions.setter
    def actions(self, *acts):
        """Set the actions."""
        self._action_list_strings = acts
        self._action_list = ActionList.parse(acts)

    @property
    def as_string_list(self):
        """Return the ActionList as a list of strings."""
        return self._action_list_strings
