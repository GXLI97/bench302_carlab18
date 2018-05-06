import time
import math
import sys
from a_star import AStar
from statistics import mean, median

def semicircle(a_star, radius, rightTurn=1, Ki=.04, Kp=1.3):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536

    errsum = 0

    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    (Lprev, Rprev) = (Linit, Rinit)

    Lfinal = Linit + (radius + BOTDIAM/2*rightTurn)/WHEELDIAM*ENCODERTICKS*1000/math.pi
    Rfinal = Rinit + (radius - BOTDIAM/2*rightTurn)/WHEELDIAM*ENCODERTICKS*1000/math.pi

    (Lprev, Rprev) = (Linit, Rinit)
    while 1:
        
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()

        if (Lcurr < Lfinal or Rcurr < Rfinal):
            a_star.motors(0, 0)
            break

        # calculate errors (leaning left)
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) - ((Rcurr - Rprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) 
        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = 105  - errsig
        motorR = 100  + errsig
        a_star.motors(int(motorL), int(motorR))
        # print("Motors on {} {}".format(int(motorL), int(motorR)))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.05)

def main():
    DEBUG = True
    if len(sys.argv) >= 3:
        Ki = float(sys.argv[2])
        Kp = float(sys.argv[1])
    else:
        Ki=.04
        Kp=1.3
    # initialize our AStar motor controller.
    a_star = AStar()

    semicircle(a_star, 1, Ki=Ki, Kp=Kp)


if __name__ == '__main__':
    main()





