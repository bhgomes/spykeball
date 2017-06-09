"""Current Testing Suite."""

from spykeball.player import Player
from spykeball.game import Game
from spykeball.touch import TouchType

P1 = Player("Billy")
P2 = Player("Bobby")
P3 = Player("Max")
P4 = Player("Cole")

G1 = Game(P1, P2, P3, P4)

print(TouchType.SET)
print(TouchType.SET.init)
print(TouchType.SET.next)
