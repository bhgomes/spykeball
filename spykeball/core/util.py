"""Core for spykeball."""


class UIDObject(object):
    """A Unique Identifier for Each Subclass."""

    _obj_uid_list = []
    _obj_uid_counter = -1

    def __init__(self, object_uid=None):
        """Create the object_uid."""
        if object_uid is None:
            if UIDObject._obj_uid_counter + 1 in UIDObject._obj_uid_list:
                UIDObject._obj_uid_counter = 1 + max(UIDObject._obj_uid_list)
            else:
                UIDObject._obj_uid_counter += 1
            object_uid = UIDObject._obj_uid_counter
        if object_uid in UIDObject._obj_uid_list:
            raise IndexError("No two UIDObjects can have the same object_uid")
        self._object_uid = object_uid
        UIDObject._obj_uid_list.append(object_uid)

    def get_uid(self):
        """Return the object_uid."""
        return self._object_uid
