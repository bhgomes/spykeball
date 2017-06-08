"""Core for spykeball."""


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
