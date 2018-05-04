from a_star import AStar
import time
import math
import sys



def turn(a_star, degrees):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.


    ticks = BOTDIAM * degrees * ENCODERTICKS / 360.0 / WHEELDIAM

    l = a_star.read_encoders()[0]
    r = a_star.read_encoders()[1]

    a_star.motors(25, -25)
    while 1:
        e = a_star.read_encoders()
        if abs(e[1]-r) + abs(e[0]-l) > 2 * ticks:
            a_star.motors(0, 0)
            return
        time.sleep(0.05)

def main():
    a_star = AStar()
    if not len(sys.argv) == 2:
        turn(a_star, 90)

    else:
        turn(a_star, sys.argv[1])

if __name__ == '__main__':
    main()