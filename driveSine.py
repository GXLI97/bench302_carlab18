import time
import math
import sys
from a_star import AStar
from statistics import mean, median

def driveSine(a_star, amplitude, periods=1, dist=1, timeout=30 Ki=.04, Kp=1.3):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536

    errsum = 0

    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    (Lprev, Rprev) = (Linit, Rinit)
    startTime = time.time()
    endTime = startTime + timeout
    while 1:
        if time.time() - startTime > endTime:
            a_star.motors(0, 0)
            break
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()

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

    driveSine(a_star, amplitude, Ki=Ki, Kp=Kp)


if __name__ == '__main__':
    main()





