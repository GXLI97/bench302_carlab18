from a_star import AStar

import time
import math
import sys

a_star = AStar()

def wiggle(forward = 1):
    a_star.motors(100, 150)
    time.sleep(2)
    a_star.motors(180, 100)
    time.sleep(2)
    a_star.motors(100, 150)
    time.sleep(2)
    a_star.motors(180, 100)
    time.sleep(2)
    a_star.motors(0, 0)

def main():
    a_star = AStar()
    wiggle(sys.argv[1])

if __name__ == '__main__':
    main()

