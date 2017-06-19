"""Current Testing Suite."""

from spykeball import Game, Player, ActionList
from spykeball.stat import DefaultStatModel

p1 = Player("Billy", 83034839)
p2 = Player("Bobby", 34924003)
p3 = Player("Max", 24950013)
p4 = Player("Cole", 34939114)

al = ActionList.load('demo/sample/actions/action000.txt')

al.players = p1, p2, p3, p4
# auto update parser

al2 = ActionList(p1, p2, p3, p4, *al.as_strings)

# print(al2)

al2.save('demo/sample/actions/action000.json')

g1 = Game(p1, p2, p3, p4, DefaultStatModel, al)
