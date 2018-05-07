from a_star import AStar

import time
import math
import sys

OVERFLOW_BUFF = 65536

def wiggle(a_star, ampl=50, per=0.01, dist=1, forward=1, DEBUG=False):
    # drives straight for dist meters.
    Kp = 1.5
    Ki = .02
    L, R = 110 * forward, 100 * forward
    errsum = 0

    if DEBUG:
        print("Driving forward this far: {}".format(forward*dist))
    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()
    (Lprev, Rprev) = (Linit, Rinit)

    i = 0

    start = time.time()
    end = start + 10
    while time.time() < end:
        i += 1
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()
        # print("Encoder values: {} {}".format(Lcurr, Rcurr))
        # calculate errors (leaning left)
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) - ((Rcurr - Rprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) + ampl*math.sin(per * i)

        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = 110 * forward - errsig
        motorR = 100 * forward + errsig
        a_star.motors(int(motorL), int(motorR))
        # print("Motors on {} {}".format(int(motorL), int(motorR)))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.01)
    a_star.motors(0, 0)

def main():
    a_star = AStar()
    if len(sys.argv) == 2:
        wiggle(a_star, float(sys.argv[1]))
    elif len(sys.argv) == 3:
        wiggle(a_star, float(sys.argv[1]), float(sys.argv[2]))
    else:
        wiggle(a_star)

if __name__ == '__main__':
    main()

