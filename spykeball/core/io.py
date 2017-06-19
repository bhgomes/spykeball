"""Spykeball IO Module."""

import json

from abc import ABCMeta, abstractmethod
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


def ext_matches(fp, *ext):
    """Return true if filename ends with any of the extensions given."""
    return fp.lower().endswith(ext)


class JSONSerializable(metaclass=ABCMeta):
    """Creates a JSON Serializable Object."""

    @abstractmethod
    def to_json(self, *args, **kwargs):
        """Encode the object into valid JSON."""

    @classmethod
    @abstractmethod
    def from_json(cls, data, *args, **kwargs):
        """Decode the object from valid JSON."""

    def __repr__(self):
        """Representation of the Object."""
        return str(self.to_json())

    def save(self, fp, *args, **kwargs):
        """Save JSON data using JSONSerializable Structure."""
        def serializer(o):
            return o.to_json(*args, **kwargs) if o is self else o.to_json()

        with open(fp, "w+") as file:
            json.dump(self, file, default=serializer, indent=4)

    @classmethod
    def load(cls, fp, *args, **kwargs):
        """Load JSON data into a JSONSerializable Structure."""
        with open(fp, "r+") as file:
            return cls.from_json(json.load(file), *args, **kwargs)
