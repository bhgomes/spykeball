"""
spykeball

Usage:
    spykeball <id>
    spykeball login [(<username> <password>)]
    spykeball game new <p1> <p2> <p3> <p4> [<actions>]
    spykeball game <id>
    spykeball player new <name> [<stats>]
    spykeball player <id>
    spykeball (-i | -h | --help | --version)

Options:
    -h --help     Show this help message.
    --version     Show version.
    -i            Open spykeball in interactive mode.
"""

from docopt import docopt
from pathlib import Path

from .game import *
from .io import *
from .model import *
from .player import *
from .touch import *
from .util import *

__all__ = (game.__all__ +
           io.__all__ +
           model.__all__ +
           player.__all__ +
           touch.__all__ +
           util.__all__)

LOCAL_STORAGE = '.spyke/'
LOCAL_PLAYER_STORAGE = 'player-data/'
LOCAL_GAME_STORAGE = 'game-data/'


def main():
    """Spykeball Main CLI Function."""
    options = docopt(__doc__,
                     version=findfile('VERSION', fail='0.0.0', strip=True))

    storage = _create_local_storage()

    if options['game']:
        if options['new']:
            pmap = PlayerMap(
                _load_from_store(storage, options['p1']),
                _load_from_store(storage, options['p2']),
                _load_from_store(storage, options['p3']),
                _load_from_store(storage, options['p4'])
                )
            home_team = Team(pmap.p1, pmap.p2)
            away_team = Team(pmap.p3, pmap.p4)

            actions = None
            if options['actions']:
                actions = Path(options['actions'])
                if actions.is_file():
                    actions = touch.load(options['actions'])
                else:
                    raise TouchMapException("{} is not a touchmap file."
                                            .format(options['actions']))

            game = Game(pmap.p1, pmap.p2, pmap.p3, pmap.p4, actions)
        else:
            if Game.valid_id(options['id']):
                game = _load_from_store(storage, options['id'])
            else:
                raise Exception("IDK")
    elif options['player']:
        if options['new']:
            player = Player(options['name'])
            with_stats = False
            stats = Path(options['stats'])
            if stats.is_file():
                pass
            elif stats.is_dir():
                pass
            else:
                pass
            _save_to_store(storage, player, with_stats=with_stats)
        else:
            if Player.valid_id(options['id']):
                player = _load_from_store(storage, options['id'])
            else:
                raise Exception("IDK")
    elif options['login']:
        print("LOGIN FAILED")
    else:
        print("BAD ARGS")


def _create_local_storage():
    """Adds local storage option for data storage of spykeball statistics."""
    storage_target = Path.home().joinpath(LOCAL_STORAGE)
    storage_target.mkdir(exist_ok=True)
    storage_target.joinpath(LOCAL_PLAYER_STORAGE).mkdir(exist_ok=True)
    storage_target.joinpath(LOCAL_GAME_STORAGE).mkdir(exist_ok=True)
    return storage_target


def _save_to_store(store, obj, ext='.json', **kwargs):
    obj.save(store.joinpath(obj.UID, ext), **kwargs)


def _load_from_store(store, uid, ext='.json', **kwargs):
    if uid.upper().startswith('G'):
        return Game.load(store.joinpath(uid, ext), **kwargs)
    elif uid.upper().startswith('P'):
        return Player.load(store.joinpath(uid, ext), **kwargs)
    else:
        raise SyntaxError("Invalid UID.")
