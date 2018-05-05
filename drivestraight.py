from a_star import AStar
import time
import math
import sys

WHEEL_DIAMETER = 70 # mm
ENCODER_TICKS = 1440 
OVERFLOW_BUFF = 65536


def drive_straight(a_star, dist=1, forward=1):
    # drives straight for dist meters.
    Kp = 1.5
    Ki = .02
    L, R = 105 * forward, 100 * forward
    errsum = 0
    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    encticks = dist/WHEEL_DIAMETER*ENCODER_TICKS * 1000/math.pi # TODO: calculate distance to encoder 
    # distance to encoder:
    Lfinal = Linit + encticks * forward
    Lfinal = (Lfinal + OVERFLOW_BUFF) % OVERFLOW_BUFF
    Rfinal = Rinit + encticks * forward
    Rfinal = (Rfinal + OVERFLOW_BUFF) % OVERFLOW_BUFF

    (Lprev, Rprev) = (Linit, Rinit)
    while 1:
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
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) - ((Rcurr - Rprev + OVERFLOW_BUFF) % OVERFLOW_BUFF) 
        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = 105 * forward - errsig
        motorR = 100 * forward + errsig
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
