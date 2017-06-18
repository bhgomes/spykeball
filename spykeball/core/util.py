"""Core for spykeball."""

from collections import Sequence
from random import randrange


# not working


class staticproperty(property):
    """Static Method and Property."""

    def __get__(self, cls, owner):
        """Getter for property."""
        return staticmethod(self.fget).__get__(None, owner)()


# not working


class classproperty(property):
    """Class Method and Property."""

    def __get__(self, cls, owner):
        """Getter for property."""
        return classmethod(self.fget).__get__(cls, owner)()


class UIDObject(object):
    """A Unique Identifier for Each Subclass."""

    __obj_uid_list = []

    def __init__(self, object_uid=None):
        """Create the object_uid."""
        self.__object_uid = object_uid

        if object_uid in self.__obj_uid_list:
            raise IndexError("No two UIDObjects can have the same object_uid.",
                             self, object_uid)
        else:
            self.__object_uid = self.generate_uid(seed=object_uid)
        self.__obj_uid_list.append(self.__object_uid)

    @property
    def UID(self):
        """Return the object_uid for this Object."""
        return self.__object_uid

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
                for _ in range(0, randrange(2, 5)):
                    num = str(randrange(0, 999999))
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

    if isinstance(seq[0], Sequence):
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
