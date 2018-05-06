from a_star import AStar
import time
import math
import sys



def turn(a_star, degrees, clockwise=1, DEBUG=False):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536
    Kp = 1.3
    Ki = .04

    if DEBUG:
        print("Making a turn of {}".format(degrees))

    if degrees < 0:
        degrees = -1 * degrees
        clockwise = -1 * clockwise


    # SUS CALIBRATION HACK
    degrees *= 0.96

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
        try:
            a_star.motors(int(motorL), int(motorR))
        except:
            print("\t\tFailed to turn with motor params of {} {} and errsig of {} and errsum of {}".format(int(motorL), int(motorR), errsig, errsum))
        # print("Motors on {} {}".format(motorL, motorR))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.05)

def main():
    a_star = AStar()
    if not len(sys.argv) == 2:
        turn(a_star, 90)

    if len(sys.argv) == 2:
        turn(a_star, float(sys.argv[1]))


if __name__ == '__main__':
    main()