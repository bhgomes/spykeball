"""Current Testing Suite."""

from spykeball import touch
from spykeball import Game, Player, PlayerMap

from spykeball import util

p1 = Player("Billy")
p2 = Player("Bobby")
p3 = Player("Max")
p4 = Player("Cole")

players = PlayerMap(p1, p2, p3, p4)

g1 = Game(players, touch.load('demo/sample/actions/action001.txt'))

g1.play()

print(g1.score)

for p in players:
    print("{} :: {}".format(p, p.stats))
