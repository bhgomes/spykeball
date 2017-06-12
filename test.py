"""Current Testing Suite."""

from spykeball.core import util
from spykeball.game import Game
from spykeball.player import Player
from spykeball.stat import DefaultStatModel
from spykeball.touch import ActionList

P1 = Player("Billy", 83034839)
P2 = Player("Bobby", 34924003)
P3 = Player("Max", 24950013)
P4 = Player("Cole", 34939114)

al = ActionList(P1, P2, P3, P4,
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

g1 = Game(P1, P2, P3, P4, DefaultStatModel)

# g1.load('resources/sample/game000.csv')

g1.actions = al

g1.play(save_stats=True)

print(P3.stats)

g1.save('resources/sample/game000.json')
