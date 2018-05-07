from a_star import AStar

import time
import math
import sys

a_star = AStar()

a_star.motor(100, 150)
time.sleep(1)
a_star.motor(150, 100)
time.sleep(1)
a_star.motor(0, 0)
