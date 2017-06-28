"""Touch Tests."""

import pytest
import random

from spykeball import touch
from spykeball import util


@pytest.fixture(scope='session')
def sample_touches():
    """Generator with sample touches."""
    while True:
        min_steps = random.randint(2, 5)
        max_steps = random.randint(6, 20)
        steps = random.randint(min_steps, max_steps)
        sample = util.randstring(steps, source=touch.TOUCHMAP_LEXICON)
        result = touch.valid_touchmap(sample)
        if result.valid:
            yield result


@pytest.fixture(scope='session')
def sample_points(sample_touches):
    """Generator with sample points."""
    while True:
        min_points = random.randint(7, 21)
        max_points = random.randint(22, 41)
        points = random.randint(min_points, max_points)
        point_array = []
        for _ in range(points):
            point_array.append(sample_touches)
        yield point_array
