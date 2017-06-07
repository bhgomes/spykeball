"""Exception classes."""


class InvalidPlayerException(Exception):
    """Raise if a player is invalid."""

    def __init__(self, message, player, *args):
        """Initialize with the invalid player."""
        self.message = message
        self.player = player
        super().__init__(message, player, *args)


class InvalidGameException(Exception):
    """Raise if a game is invalid."""

    def __init__(self, message, game, *args):
        """Initialize with the invalid game."""
        self.message = message
        self.game = game
        super().__init__(message, game, *args)
