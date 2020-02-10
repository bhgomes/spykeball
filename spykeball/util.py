"""Core for spykeball."""

__all__ = ['default_typeerror', 'typecheck', 'isinnertype', 'isnestedtype',
           'haskeys', 'flatten', 'groupby', 'randstring', 'UIDObject']

import string
import random

from collections import Iterable, Sequence
from itertools import zip_longest


def default_typeerror(obj, *types):
    """Return default TypeError."""
    return TypeError("Type mismatch. Input type should be "
                     "'{}' but is '{}'.".format(types, type(obj)))


def typecheck(obj, *types, error=TypeError, msg=None):
    """Throw exception if object is not of a certain type."""
    value = isinstance(obj, types)
    if not value and error is not None:
        if msg is None:
            try:
                raise default_typeerror(obj, *types)
            except TypeError as e:
                raise error(str(e), obj, *types)
        else:
            raise error(msg, obj, *types)
    return value


def isinnertype(obj, classinfo, error=None, msg=None):
    """Return true if all items in object are of a certain type."""
    value = True
    if isinstance(classinfo, Iterable):
        value = True
        for c in classinfo:
            value = value or all(typecheck(e, c, error=error, msg=msg)
                                 for e in obj)
        return value
    else:
        return all(typecheck(e, classinfo, error=error, msg=msg) for e in obj)


def isnestedtype(obj, seqtype, nestedtype, error=None, msg=None):
    """Return true if object is a collection of a certain type."""
    return (typecheck(obj, seqtype, error=error, msg=msg)
            and isinnertype(obj, nestedtype, error=error, msg=msg))


def haskeys(d, *keys, error=None, msg=None, validate_dict=True):
    """Return true if the object has these keys."""
    if validate_dict:
        typecheck(d, dict)

    value = all(k in d for k in keys)
    if not value and error is not None:
        msg = "Keys '{}' not found.".format(keys) if msg is None else msg
        raise error(msg, d, keys)
    return value


def flatten(l):
    """Flatten a list of elements."""
    for e in l:
        if isinstance(e, Sequence) and not isinstance(e, (str, bytes)):
            yield from flatten(e)
        else:
            yield e


def groupby(iterable, chunksize, fillvalue=None):
    """Group an iterable by given amount."""
    return zip_longest(*([iter(iterable)] * chunksize), fillvalue=fillvalue)


def randstring(n=1, source=None):
    """Generate a random string of length 'n' from 'source'."""
    if not source:
        source = string.ascii_letters + string.digits
    if n <= 0:
        raise ValueError("Length of sequence must be greater than 0.", n)
    return ''.join(random.choices(source, k=n))


class UIDObject(object):
    """A Unique Identifier for Each Subclass."""

    _obj_uid_list = []

    def __init__(self, object_uid=None, **kwargs):
        """Create the object_uid."""
        self._object_uid = object_uid

        if object_uid in self.__class__._obj_uid_list:
            raise IndexError("No two UIDObjects can have the same object_uid.",
                             self, object_uid)
        else:
            self._object_uid = self.generate_uid(seed=object_uid)
        self.__class__._obj_uid_list.append(self._object_uid)
        super().__init__(**kwargs)

    def __del__(self):
        """Deleting a UIDObject removes its id from the __obj_uid_list."""
        index = self.__class__._obj_uid_list.index(self.UID)
        del self.__class__._obj_uid_list[index]

    @property
    def UID(self):
        """Return the object_uid for this Object."""
        return self._object_uid

    @property
    def UID_num(self):
        """Return the numeric component of the object_uid for this Object."""
        return int(''.join(self._object_uid.split('-')[1:]))

    @classmethod
    def generate_uid(cls, seed=None):
        """Generate a Unique ID."""
        class_letter = cls.__name__[0]
        if isinstance(seed, int):
            num = list(str(seed))
            result = []
            while len(num) > 0:
                result.append('-' + ''.join(num[:6]) + '0' * (6-len(num[:6])))
                del num[:6]
            return class_letter + ''.join(result)
        elif isinstance(seed, str):
            try:
                if cls.valid_id(seed):
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
            test_uid = ''
            first_loop = True
            while first_loop or test_uid in cls._obj_uid_list:
                first_loop = False
                num_list = []
                for _ in range(0, random.randrange(1, random.randrange(4, 8))):
                    num = str(random.randrange(0, 999999))
                    num_list.append('-' + num + '0' * (6-len(num)))
                test_uid = class_letter + ''.join(num_list)
            return test_uid

    @classmethod
    def valid_id(cls, uid):
        """Verify the Unique ID."""
        typecheck(uid, str)
        digiterror = SyntaxError("UID must contain sets of six-digit numbers.")
        uid_as_list = uid.split('-')
        if uid_as_list[0] == cls.__name__[0]:
            for num in uid_as_list[1:]:
                if len(num) != 6:
                    raise digiterror
                else:
                    try:
                        int(num)
                    except ValueError:
                        raise digiterror
            return True
        else:
            raise SyntaxError(
                "UID must begin with the same letter as the class.")
