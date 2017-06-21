"""Current Testing Suite."""

from spykeball import Game, Player, ActionList

p1 = Player("Billy")
p2 = Player("Bobby")
p3 = Player("Max")
p4 = Player("Cole")

players = p1, p2, p3, p4

g1 = Game(p1, p2, p3, p4, ActionList.load('demo/sample/actions/action001.txt'))

g1.play()

print(g1.score)

for p in players:
    print("{} :: {}".format(p, p.stats))
