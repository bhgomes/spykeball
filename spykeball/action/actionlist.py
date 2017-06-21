"""ActionList Class."""

from spykeball.core import io
from spykeball.core import util
from spykeball.core.exception import (
    PlayerException,
    JSONKeyError,
)
from spykeball.player import Player
from spykeball.action.touchmap import parse


class ActionList(util.PlayerInterface, io.JSONSerializable):
    """List of actions."""

    def __init__(self, p1, p2, p3, p4, *actions):
        """Instantiate an ActionList."""
        super().__init__(p1, p2, p3, p4)
        self._action_strings = list(actions)

        if p1 and p2 and p3 and p4:
            self._actionlist = parse(p1, p2, p3, p4, *actions)
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
                self._actionlist[key] = parse(
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

    def register_players(self, ps):
        """Register players and parses ActionList."""
        self.players = ps
        self._actionlist = parse(
            self._p1, self._p2, self._p3, self._p4, *self._action_strings)
        self._parsed = True

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
        """Return the list of actions."""
        return self._actionlist if self._parsed else self._action_strings

    @actions.setter
    def actions(self, *acts):
        """Set the actions."""
        self._action_strings = list(acts)
        if self._parsed:
            self._actionlist = parse(
                self._p1, self._p2, self._p3, self._p4, *acts)

    @property
    def as_strings(self):
        """Return the ActionList as a list of strings."""
        return self._action_strings

    @property
    def parsed(self):
        """Return true if ActionList has been parsed."""
        return self._parsed

    def to_json(self, with_touches=True):
        """Encode the object into valid JSON."""
        actionlist = {
            "class": "ActionList",
            "strings": self._action_strings
        }

        if with_touches and self._parsed:
            actionlist['players'] = {
                'p1': self._p1, 'p2': self._p2, 'p3': self._p3, 'p4': self._p4}
            actionlist['touches'] = self._actionlist

        return actionlist

    @classmethod
    def from_json(cls, data, with_touches=True):
        """Decode the object from valid JSON."""
        actionlist = None
        if util.has_keys(data, 'class', 'strings', error=JSONKeyError):
            if with_touches:
                if util.has_keys(data, 'players', 'touches',
                                 error=JSONKeyError):

                    players = data['players']

                    if util.has_keys(players, 'p1', 'p2', 'p3', 'p4',
                                     error=JSONKeyError):
                        p1 = Player.from_json(players['p1'])
                        p2 = Player.from_json(players['p2'])
                        p3 = Player.from_json(players['p3'])
                        p4 = Player.from_json(players['p4'])
                        actionlist = cls(p1, p2, p3, p4, data['strings'])
            else:
                actionlist = cls.from_strings(data['strings'])

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
