"""Statistics Module."""

from spykeball.core.exception import InvalidGameException


class GameInterpreter(object):
    """Interpret a game."""

    def __init__(self, action_list):
        pass


def player_score(player, game, game_interpreter=None):
    """Determine the score of a player given their performance in a game."""
    if not isinstance(game.length, int) or (game.length < 21):
        raise InvalidGameException(
            "Game has an invalid length. Shoud be 21 or greater.",
            game,
            game.length
        )

    game_length_weight = 1 if game.length <= 39 else 39.0/game.length

    # extract the following from the game

    spikes_returned = 0
    total_spikes = 0
    d_touch_nr = 0
    d_touch_r = 0
    aces = 0
    aced = 0
    serves_made = 0
    total_serves = 0
    missed_sets = 0
    ok_sets = 0
    missed_spikes = 0

    hitting = 20 * (1 - spikes_returned/total_spikes)
    defense = (d_touch_nr + 0.4 * hitting * d_touch_r) * game_length_weight
    serving = 5.5 * aces + 15 * (serves_made/total_serves)
    cleanliness = \
        20 - 5 * (missed_sets + missed_spikes) - 0.5 * ok_sets - 2 * aced

    return hitting + defense + serving + cleanliness
