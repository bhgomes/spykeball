"""Core for spykeball."""

import string

from collections import Sequence

try:
    import random.SystemRandom as random
except Exception:
    import random


class UIDObject(object):
    """A Unique Identifier for Each Subclass."""

    __obj_uid_list = []

    def __init__(self, object_uid=None, **kwargs):
        """Create the object_uid."""
        self.__object_uid = object_uid

        if object_uid in self.__obj_uid_list:
            raise IndexError("No two UIDObjects can have the same object_uid.",
                             self, object_uid)
        else:
            self.__object_uid = self.generate_uid(seed=object_uid)
        self.__obj_uid_list.append(self.__object_uid)
        super().__init__(**kwargs)

    @property
    def UID(self):
        """Return the object_uid for this Object."""
        return self.__object_uid

    @property
    def UID_num(self):
        """Return the numeric component of the object_uid for this Object."""
        return int(''.join(self.__object_uid.split('-')[1:]))

    @classmethod
    def generate_uid(cls, seed=None):
        """Generate a Unique ID."""
        out = cls.__name__[0]
        if isinstance(seed, int):
            num = list(str(seed))
            result = []
            while len(num) > 0:
                result.append('-' + ''.join(num[:6]) + '0' * (6-len(num[:6])))
                del num[:6]
            out += ''.join(result)
        elif isinstance(seed, str):
            try:
                if cls.verify_uid(seed):
                    return seed
            except Exception:
                num_list = []
                for e in seed:
                    try:
                        num_list.append(str(int(e)))
                    except ValueError:
                        pass
                return cls.generate_uid(seed=int(''.join(num_list)))
        else:
            test_uid = ""
            first_loop = True
            while first_loop or test_uid in cls.__obj_uid_list:
                first_loop = False
                num_list = []
                for _ in range(0, random.randrange(1, random.randrange(4, 8))):
                    num = str(random.randrange(0, 999999))
                    num_list.append('-' + num + '0' * (6-len(num)))
                test_uid = out + ''.join(num_list)
            out = test_uid
        return out

    @classmethod
    def verify_uid(cls, uid):
        """Verify the Unique ID."""
        if isinstance(uid, str):
            uid_as_list = uid.split('-')
            if uid_as_list[0] == cls.__name__[0]:
                for num in uid_as_list[1:]:
                    if len(num) != 6:
                        raise SyntaxError(
                            "UID must contain sets of six-digit numbers.")
                    else:
                        try:
                            int(num)
                        except ValueError:
                            raise SyntaxError(
                                "UID must contain sets of six-digit numbers.")
                return True
            else:
                raise SyntaxError(
                    "UID must begin with the same letter as the class.")
        else:
            raise TypeError("UID is not a string.")


class PlayerInterface(object):
    """Implements gets and sets for each player."""

    def __init__(self, p1, p2, p3, p4, **kwargs):
        """Add each player to the Interface."""
        self.players = p1, p2, p3, p4
        self._players_set = p1 and p2 and p3 and p4
        # use ^ to auto update
        super().__init__(**kwargs)

    @property
    def p1(self):
        """Return Player 1."""
        return self._p1

    @p1.setter
    def p1(self, new_p1):
        """Set Player 1."""
        self._p1 = new_p1
        self._players['p1'] = new_p1
        self._teams['home'] = (new_p1, self._p2)

    @property
    def p2(self):
        """Return Player 2."""
        return self._p2

    @p2.setter
    def p2(self, new_p2):
        """Set Player 2."""
        self._p2 = new_p2
        self._players['p2'] = new_p2
        self._teams['home'] = (self._p1, new_p2)

    @property
    def p3(self):
        """Return Player 3."""
        return self._p3

    @p3.setter
    def p3(self, new_p3):
        """Set Player 3."""
        self._p3 = new_p3
        self._players['p3'] = new_p3
        self._teams['away'] = (new_p3, self._p4)

    @property
    def p4(self):
        """Return Player 4."""
        return self._p4

    @p4.setter
    def p4(self, new_p4):
        """Set Player 4."""
        self._p4 = new_p4
        self._players['p4'] = new_p4
        self._teams['away'] = (self._p3, new_p4)

    @property
    def players(self):
        """Return players of the game."""
        return self._players

    @players.setter
    def players(self, ps):
        """Set the players."""
        if isinstance(ps, (tuple, list)):
            self._p1 = ps[0]
            self._p2 = ps[1]
            self._p3 = ps[2]
            self._p4 = ps[3]
            self._players = {
                "p1": ps[0], "p2": ps[1], "p3": ps[2], "p4": ps[3]
                }
            self._teams = {"home": (ps[0], ps[1]), "away": (ps[2], ps[3])}
        elif isinstance(ps, dict) and has_keys(ps, 'p1', 'p2', 'p3', 'p4'):
            self._players = ps
            self._p1 = ps['p1']
            self._p2 = ps['p2']
            self._p3 = ps['p3']
            self._p4 = ps['p4']
            self._teams = {
                "home": (ps['p1'], ps['p2']), "away": (ps['p3'], ps['p4'])
                }
        else:
            raise TypeError("Input to players has wrong type.", ps, type(ps))

    @property
    def home_team(self):
        """Return home team of the game."""
        return self._teams['home']

    @property
    def away_team(self):
        """Return away team of the game."""
        return self._teams['away']


def has_keys(d, *keys, error=None):
    """Return true if the dictionary has these keys."""
    value = all(k in d for k in keys)
    if not value and error is not None:
        raise error(d, keys)
    return value


def flatten(l):
    """Flatten a list of elements."""
    for e in l:
        if isinstance(e, Sequence) and not isinstance(e, (str, bytes)):
            yield from flatten(e)
        else:
            yield e


def join(seq):
    """Join a list of elements into a single element."""
    if not isinstance(seq, Sequence):
        raise ValueError("Input is not a Sequence.", seq)

    if not seq:
        return seq

    if isinstance(seq[0], Sequence) and not isinstance(seq[0], str):
        return list(flatten(seq))
    else:
        out = []
        for e in seq:
            try:
                out.append(str(e))
            except ValueError:
                raise ValueError("Sequence cannot be joined.", seq)
        try:
            if isinstance(seq[0], int):
                for e in seq:
                    if isinstance(e, float):
                        seq[0] = float(seq[0])
                        break
            return type(seq[0])(''.join(out))
        except Exception:
            raise ValueError("Sequence cannot be joined.", seq)


def randstring(n=0, source=None):
    """Generate a random string of length 'n' from 'source'."""
    if not source:
        source = string.ascii_letters + string.digits
    if n <= 0:
        n = len(source)
    return ''.join(random.choice(source, k=n))
