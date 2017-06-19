"""Exception classes."""


class PlayerException(Exception):
    """Raise an exception about a player."""

    def __init__(self, message, player, *args):
        """Initialize with the player."""
        self.message = message
        self.player = player
        super().__init__(message, player, *args)


class GameException(Exception):
    """Raise an exception about a game."""

    def __init__(self, message, game, *args):
        """Initialize with the game."""
        self.message = message
        self.game = game
        super().__init__(message, game, *args)


class TouchMapException(Exception):
    """Raise an exception about a touch map."""

    def __init__(self, message, touch_string, *args):
        """Initialize with the touch map."""
        self.message = message
        self.touch_string = touch_string
        super().__init__(message, touch_string, *args)


class JSONKeyError(Exception):
    """Raise if a KeyError occurs during JSON Processing."""

    def __init__(self, data, proper_keys, *args):
        """Initialize with the invalid key."""
        self.data = data
        self.proper_keys = proper_keys
        self.given_keys = data.keys()
        self.message = ("JSON input, '{}', does not have valid keys. "
                        "'{}' must include {} but instead has {}.").format(
                            data, data, proper_keys, self.given_keys)
        super().__init__(
            self.message, data, proper_keys, self.given_keys, *args)
