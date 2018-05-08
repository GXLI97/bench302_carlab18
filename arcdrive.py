import time
import math
import sys
from a_star import AStar
from statistics import mean, median

def arcdrive(a_star, radius, leftTurn=1, arc=180, speed=1, forward=1,Kp = 1.8,Ki = 0.1):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536
    

    errsum = 0

    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    (Lprev, Rprev) = (Linit, Rinit)

    Lfinal = Linit + (1000*radius - leftTurn*BOTDIAM/2)/WHEELDIAM*ENCODERTICKS*(arc/180.)*forward
    Rfinal = Rinit + (1000*radius + leftTurn*BOTDIAM/2)/WHEELDIAM*ENCODERTICKS*(arc/180.)*forward
    print("Linit: {}\tLfinal: {}\tRinit: {}\tRfinal: {}".format(Linit, Lfinal, Rinit,Rfinal))

    (Lprev, Rprev) = (Linit, Rinit)
    while 1:
        
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()

        if forward == 1 and (Lcurr > Lfinal or Rcurr > Rfinal):
            print("Lcurr: {}\tLfinal: {}\tRcurr: {}\tRfinal: {}".format(Lcurr, Lfinal, Rcurr, Rfinal))
            break
        if forward == -1 and (Lcurr < Lfinal or Rcurr < Rfinal):
            print("Lcurr: {}\tLfinal: {}\tRcurr: {}\tRfinal: {}".format(Lcurr, Lfinal, Rcurr, Rfinal))
            break

        # calculate errors (leaning left)
        # missing logic here to actually make the turn
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF)*(1000*radius + leftTurn*BOTDIAM/2)/(1000*radius) - ((Rcurr - Rprev + OVERFLOW_BUFF) % OVERFLOW_BUFF)*(1000*radius - leftTurn*BOTDIAM/2)/(1000*radius)
        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = speed*105*forward - errsig
        motorR = speed*100*forward + errsig
        a_star.motors(int(motorL), int(motorR))
        # print("Motors on {} {}".format(int(motorL), int(motorR)))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.05)

    a_star.motors(0,0)

def main():
    DEBUG = True
    forward = 1
    leftTurn=1
    arc=180
    radius=1.0/4
    speed=1.5
    ki = 0.1
    kp = 2.0
    if len(sys.argv) >= 6:
        forward = float(sys.argv[5])
        speed = float(sys.argv[4])
        leftTurn = float(sys.argv[3])
        arc = float(sys.argv[2])
        radius = float(sys.argv[1])
    elif len(sys.argv) >= 4:
        radius = float(sys.argv[3])
        ki = float(sys.argv[2])
        kp =float(sys.argv[1])
    elif len(sys.argv) >= 3:
        ki = float(sys.argv[2])
        kp =float(sys.argv[1])

    # initialize our AStar motor controller.
    a_star = AStar()

    arcdrive(a_star, radius=radius, leftTurn=leftTurn, arc=arc, speed=speed, forward=forward, Ki=ki, Kp=kp)
    arcdrive(a_star, radius=radius, leftTurn=leftTurn*-1, arc=arc, speed=speed, forward=forward, Ki=ki, Kp=kp)
    arcdrive(a_star, radius=radius, leftTurn=leftTurn, arc=arc, speed=speed, forward=forward, Ki=ki, Kp=kp)
    arcdrive(a_star, radius=radius, leftTurn=leftTurn*-1, arc=arc, speed=speed, forward=forward, Ki=ki, Kp=kp)

    a_star.motors(0,0)

if __name__ == '__main__':
    main()





