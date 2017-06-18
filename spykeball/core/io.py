"""Spykeball IO Module."""

from abc import ABCMeta, abstractmethod
from json import dump
from spykeball.core import util


def readsplit(fp, *delimeters, buffer_size=4096):
    """Read a file and yield the content separated by delimeters."""
    if len(delimeters) == 0:
        delimeters = ('\n')

    if fp.closed:
        raise IOError("File is not open.", fp)

    buffer = ''
    while True:
        new_buffer = fp.read(buffer_size)
        if len(new_buffer) == 0:
            yield buffer
            return
        buffer += new_buffer
        lines = buffer.split(delimeters[0])
        for delim in delimeters[1:]:
            lines = list(util.flatten(map(lambda e: e.split(delim), lines)))
        for line in lines[:-1]:
            yield line
        buffer = lines[-1]


class JSONSerializable(metaclass=ABCMeta):
    """Creates a JSON Serializable Object."""

    @abstractmethod
    def to_json(self):
        """Encode the object into valid JSON."""

    @abstractmethod
    def from_json(self, s):
        """Decode the object from valid JSON."""

    def __repr__(self):
        """Representation of the Object."""
        return str(self.to_json())

    def save(self, fp, *args, **kwargs):
        """Save JSON data using JSONSerializable Structure."""
        def serializer(o):
            return o.to_json(*args, **kwargs) if o is self else o.to_json()

        with open(fp, "w+") as file:
            dump(self, file, default=serializer, indent=4)

    @classmethod
    def load(cls, fp, *args, **kwargs):
        """Load JSON data into a JSONSerializable Structure."""
        # use from_json function


# def save_json(fp, obj, *args, **kwargs):
#     """Save JSON data using JSONSerializable Structure."""
#     def serializer(o):
#         return o.to_json(*args, **kwargs) if o is obj else o.to_json()
#
#     with open(fp, "w+") as file:
#         dump(obj, file, default=serializer, indent=4)
