"""Current Testing Suite."""

# from spykeball.core import util
from spykeball.game import Game
from spykeball.player import Player
from spykeball.stat import DefaultStatModel
from spykeball.touch import ActionList

p1 = Player("Billy", 83034839)
p2 = Player("Bobby", 34924003)
p3 = Player("Max", 24950013)
p4 = Player("Cole", 34939114)

al = ActionList(p1, p2, p3, p4,
                "1343121p",
                "143412n",
                "3121p",
                "234321s23w43p",
                "4a1",
                "4n",
                "14342123431213w4n",
                "1a3",
                "13432w1s2p"
                )

g1 = Game(p1, p2, p3, p4, DefaultStatModel, al)
