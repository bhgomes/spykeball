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

__version__ = '0.0.27'  # temporary while fixing VERSION Scanning

ROOT = Path(__file__).parent
HOME = Path.home()
LOCAL_STORAGE = HOME.joinpath('.spyke')
LGAMESTORE = LOCAL_STORAGE.joinpath('game-data')
LPLAYERSTORE = LOCAL_STORAGE.joinpath('player-data')


def main():
    """Spykeball Main CLI Function."""
    options = docopt(__doc__, version=__version__)

    LOCAL_STORAGE.mkdir(exist_ok=True)
    LGAMESTORE.mkdir(exist_ok=True)
    LPLAYERSTORE.mkdir(exist_ok=True)

    storage = LOCAL_STORAGE

    if options['game']:
        if options['new']:
            pmap = PlayerMap(
                _load_from_store(LPLAYERSTORE, options['<p1>']),
                _load_from_store(LPLAYERSTORE, options['<p2>']),
                _load_from_store(LPLAYERSTORE, options['<p3>']),
                _load_from_store(LPLAYERSTORE, options['<p4>'])
                )
            home_team = Team(pmap.p1, pmap.p2)
            away_team = Team(pmap.p3, pmap.p4)

            rallies = None
            if options['actions']:
                rally_file = Path(options['<actions>'])
                if rally_file.is_file():
                    rallies = touch.load(options['<actions>'])
                else:
                    raise RallyException("{} is not a touchmap file."
                                         .format(rally_file))

            game = Game(pmap, rallies)
        else:
            if Game.valid_id(options['<id>']):
                game = _load_from_store(LGAMESTORE, options['<id>'])
            else:
                raise Exception("IDK")
    elif options['player']:
        if options['new']:
            player = Player(options['<name>'])
            with_stats = False
            if options['<stats>']:
                stats = Path(options['<stats>'])
                if stats.is_file():
                    pass
                elif stats.is_dir():
                    pass
                else:
                    pass
            _save_to_store(LPLAYERSTORE, player, with_stats=with_stats)
        else:
            if Player.valid_id(options['<id>']):
                player = _load_from_store(LPLAYERSTORE, options['<id>'])
            else:
                raise Exception("IDK")
    elif options['login']:
        print("LOGIN FAILED")
    else:
        print(__doc__)


def _save_to_store(store, obj, ext='.json', **kwargs):
    obj.save(store.joinpath(obj.UID + ext), **kwargs)


def _load_from_store(store, uid, ext='.json', **kwargs):
    if uid.upper().startswith('G'):
        return Game.load(store.joinpath(uid + ext), **kwargs)
    elif uid.upper().startswith('P'):
        return Player.load(store.joinpath(uid + ext), **kwargs)
    else:
        raise SyntaxError("Invalid UID.")
