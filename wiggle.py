from a_star import AStar

import time
import math
import sys

def wiggle(a_star):
    # start going straightish
    a_star.motors(110, 100)
    time.sleep(2)
    a_star.motors(0, 100)
    time.sleep(0.25)
    a_star.motors(110, 100)
    time.sleep(2)
    a_star.motors(110, 0)
    time.sleep(0.25)
    a_star.motors(110, 100)

def main():
    a_star = AStar()
    wiggle(a_star)

if __name__ == '__main__':
    main()

