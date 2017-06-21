"""Spykeball TouchMap Parse Method."""

from collections import deque

from spykeball.action.touch import (
    Service,
    Defense,
    Set,
    Spike,
    TouchError
)
from spykeball.core.exception import (
    PlayerException,
    TouchMapException,
)


def parse(p1, p2, p3, p4, *actions):
    """Parse actions into AbstractTouches."""
    # reqwite parse to include error (e) and convert double touches to
    # no-point

    output = []

    def pmap(player):
        out = {'1': p1, '2': p2, '3': p3, '4': p4}.get(player)
        if out is None:
            raise PlayerException(
                "Player is not part of this player list.",
                player, (p1, p2, p3, p4))
        else:
            return out

    for point in actions:
        touches = []
        touch = Service

        focus = None
        same_team = ('1', '2')
        other_team = ('3', '4')

        action_deque = deque(point)

        def next_touch():
            return action_deque.popleft()

        def verify_action_deque_empty(error_on=False):
            if error_on:
                if len(action_deque) == 0:
                    raise TouchMapException("No ending character.", point)
            elif len(action_deque) != 0:
                raise TouchMapException("Touch past end of play.", point)

        def set_focus(player):
            nonlocal focus
            nonlocal same_team
            nonlocal other_team

            focus = player

            if focus not in same_team:
                if focus in other_team:
                    same_team, other_team = other_team, same_team
                else:
                    raise TouchMapException(
                        "Team collision.", point, focus, same_team, other_team)

        while len(action_deque) != 0:
            if touch is Service:
                set_focus(next_touch())
                modifier = next_touch()

                if modifier == 'n':
                    touches.append(Service(pmap(focus), success=False))
                    verify_action_deque_empty(error_on=False)
                elif modifier == 'a':
                    target = next_touch()
                    if target in other_team:
                        touches.append(Service(pmap(focus),
                                               target=pmap(target),
                                               is_ace=True))
                    else:
                        raise TouchMapException(
                            "Player cannot ace a teammate.", point)
                    verify_action_deque_empty(error_on=False)
                elif modifier in other_team:
                    touches.append(Service(pmap(focus),
                                           target=pmap(modifier)))
                    set_focus(modifier)
                    touch = Defense
                else:
                    raise TouchMapException("Invalid character.", point)

            else:
                modifier = next_touch()

                if modifier in ('n', 'p'):
                    if modifier == 'n':
                        clz = Defense if touch is Defense else Spike
                        success = False
                    else:
                        clz = Spike
                        success = True

                    # how to determine if touch was a spike or a missed set

                    touches.append(clz(pmap(focus), success=success))
                    verify_action_deque_empty(error_on=False)

                else:
                    strength = None
                    target = modifier
                    err = None

                    if modifier in ('s', 'w'):
                        strength = modifier
                        target = next_touch()
                    elif modifier == 'e':
                        target = next_touch()
                        if target in same_team:
                            err = TouchError.FutureMistake
                        else:
                            raise TouchMapException(
                                "Invalid character.", point)

                    if target in same_team or target in other_team:
                        if target in same_team and touch is Spike:
                            if target == focus:
                                err = TouchError.DoubleTouch
                            else:
                                raise TouchMapException(
                                    "Player cannot spike a teammate.", point)

                        if target in other_team:
                            touch = Spike

                        touches.append(touch(pmap(focus),
                                             target=pmap(target),
                                             strength=strength,
                                             error=err))
                        set_focus(target)
                        touch = touch._next

                    else:
                        raise TouchMapException("Invalid character.", point)

        output.append(touches)

    return output
