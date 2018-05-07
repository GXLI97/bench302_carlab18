from a_star import AStar

import time
import math
import sys

def wiggle(a_star, dist=1, forward=1, DEBUG=False):
    # drives straight for dist meters.
    Kp = 1.5
    Ki = .02
    L, R = 215 * forward, 200 * forward
    errsum = 0

    if DEBUG:
        print("Driving forward this far: {}".format(forward*dist))
    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    encticks = dist/WHEEL_DIAMETER*ENCODER_TICKS * 1000/math.pi # TODO: calculate distance to encoder 
    # distance to encoder:
    Lfinal = Linit + encticks * forward
    Rfinal = Rinit + encticks * forward

    (Lprev, Rprev) = (Linit, Rinit)

    i = 0
    while 1:
        i += 1
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()
        # print("Encoder values: {} {}".format(Lcurr, Rcurr))
        # if we have traveled distance, stop.
        if forward == 1 and (Lcurr > Lfinal or Rcurr > Rfinal):
            a_star.motors(0, 0)
            break
        if forward == -1 and (Lcurr < Lfinal or Rcurr < Rfinal):
            a_star.motors(0, 0)
            break
        # calculate errors (leaning left)
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) - ((Rcurr - Rprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) + math.sin(i*0.05)
        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = 215 * forward - errsig
        motorR = 200 * forward + errsig
        a_star.motors(int(motorL), int(motorR))
        # print("Motors on {} {}".format(int(motorL), int(motorR)))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.05)

def main():
    a_star = AStar()
    if len(sys.argv) == 2:
        drive_straight(a_star, float(sys.argv[1]))
    elif len(sys.argv) == 3:
        drive_straight(a_star, float(sys.argv[1]), int(sys.argv[2]))
    else:
        drive_straight(a_star)

if __name__ == '__main__':
    main()

