from a_star import AStar
import time
import math
import sys



def turn(a_star, degrees, clockwise=1, Kp=1.1, Ki=.04):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536

    if degrees < 0:
        degrees = -1 * degrees
        clockwise = -1 * clockwise

    errsum = 0
    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    enticks = BOTDIAM * degrees * ENCODERTICKS / 360.0 / WHEELDIAM 
    # distance to encoder:
    Lfinal = Linit + enticks * clockwise
    Rfinal = Rinit - enticks * clockwise

    (Lprev, Rprev) = (Linit, Rinit)
    while 1:
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()
        # print("Encoder values: {} {}".format(Lcurr, Rcurr))
        # if we have traveled distance, stop.
        if clockwise == 1 and (Lcurr > Lfinal or Rcurr < Rfinal):
            a_star.motors(0, 0)
            break
        if clockwise == -1 and (Lcurr < Lfinal or Rcurr > Rfinal):
            a_star.motors(0, 0)
            break
        # calculate errors (leaning left)
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) - ((Rprev - Rcurr + OVERFLOW_BUFF) % OVERFLOW_BUFF) 
        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = 50 * clockwise - errsig
        motorR = -50 * clockwise - errsig
        a_star.motors(int(motorL), int(motorR))
        # print("Motors on {} {}".format(motorL, motorR))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.1)

def main():
    a_star = AStar()
    if not len(sys.argv) == 2:
        turn(a_star, 90)

    if len(sys.argv) == 2:
        turn(a_star, float(sys.argv[1]))


if __name__ == '__main__':
    main()