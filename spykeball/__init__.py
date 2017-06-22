"""
spykeball

Usage:
    spykeball

"""

from docopt import docopt


def main():
    """Spykeball Main CLI Function."""
    options = docopt(__doc__)
    for k, v in options.items():
        pass
