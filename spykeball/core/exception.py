"""Exception classes."""


class PlayerException(Exception):
    """Raise an exception about a player."""

    def __init__(self, message, player, *args):
        """Initialize with the player."""
        self.player = player
        self.message = message + "Player: {}".format(player)
        super().__init__(self.message, player, *args)


class GameException(Exception):
    """Raise an exception about a game."""

    def __init__(self, message, game, *args):
        """Initialize with the game."""
        self.game = game
        self.message = message + "Game: {}".format(game)
        super().__init__(self.message, game, *args)


class TouchMapException(Exception):
    """Raise an exception about a touch map."""

    def __init__(self, message, touch_map, *args):
        """Initialize with the touch map."""
        self.touch_map = touch_map
        self.message = message + "TouchMap: {}".format(touch_map)
        super().__init__(self.message, touch_map, *args)


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
