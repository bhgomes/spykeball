"""Core for spykeball."""

from abc import ABCMeta, abstractmethod

from json import JSONEncoder, JSONDecoder


class UIDObject(object):
    """A Unique Identifier for Each Subclass."""

    __obj_uid_list = []
    __obj_uid_counter = -1

    def __init__(self, object_uid=None):
        """Create the object_uid."""
        if object_uid is None:
            if UIDObject.__obj_uid_counter + 1 in UIDObject.__obj_uid_list:
                UIDObject.__obj_uid_counter = 1 + max(UIDObject.__obj_uid_list)
            else:
                UIDObject.__obj_uid_counter += 1
            object_uid = UIDObject.__obj_uid_counter
        if object_uid in UIDObject.__obj_uid_list:
            raise IndexError("No two UIDObjects can have the same object_uid")
        self.__object_uid = object_uid
        UIDObject.__obj_uid_list.append(object_uid)

    @property
    def UID(self):
        """Return the object_uid."""
        return self.__object_uid


class JSONSerializable(JSONEncoder, JSONDecoder, metaclass=ABCMeta):
    """Creates a JSON Serializable Object."""

    def serialize(o):
        """Default serialization protocol for json.dumps."""
        return o.default(o, o)

    @abstractmethod
    def to_json(self):
        """Encode the object into valid JSON."""

    @abstractmethod
    def from_json(self, s):
        """Decode the object from valid JSON."""

    def __repr__(self):
        """Representation of the Object."""
        return str(self.to_json())

    def default(self, o=None, *_):
        """Set the JSONEncoder.default to self.to_json."""
        try:
            return self.to_json()
        except TypeError:
            return self.to_json(self)

    def decode(self, s):
        """Set the JSONDecoder.decode to self.from_json."""
        return self.from_json(s)


class instclassmethod(object):
    """Instance and Classmethod Decorator."""

    def __init__(self, method):
        """Initialize Instance/Class Method."""
        self._method = method

    def __get__(self, instance, owner):
        """Return transformed method."""
        if instance is None:
            return lambda *args, **kwargs: self._method(
                owner, *args, **kwargs)
        else:
            return lambda *args, **kwargs: self._method(
                instance, *args, **kwargs)
