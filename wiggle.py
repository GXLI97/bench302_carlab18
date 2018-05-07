from a_star import AStar

import time
import math
import sys

a_star = AStar()

a_star.motors(100, 150)
time.sleep(1)
a_star.motors(150, 100)
time.sleep(1)
a_star.motors(0, 0)
