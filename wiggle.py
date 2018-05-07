from a_star import AStar

import time
import math
import sys

a_star = AStar()

a_star.motors(100, 150)
time.sleep(2)
a_star.motors(160, 100)
time.sleep(2)
a_star.motors(0, 0)
