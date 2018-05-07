from a_star import AStar

import time
import math
import sys

a_star = AStar()

def wiggle(forward = 1):
    L1, R1 = 100*forward, 150*forward
    a_star.motors(L1, R1)
    time.sleep(2)
    L2, R2 = 180*forward, 100*forward
    a_star.motors(L2, R2)
    time.sleep(2)
    a_star.motors(L1, R1)
    time.sleep(2)
    a_star.motors(L2, R2)
    time.sleep(2)
    a_star.motors(0, 0)

def main():
    a_star = AStar()
    wiggle(int(sys.argv[1]))

if __name__ == '__main__':
    main()

