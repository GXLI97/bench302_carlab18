from a_star import AStar
import time

WHEEL_DIAMETER = 70 # mm
ENCODER_TICKS = 1440 

a_star = AStar()

def drive_straight(a_star, dist, forward=True):
    # drives straight for dist meters.
    Kp = 1
    Ki = .08
    L, R = 100, 100
    errsum = 0
    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    encticks = dist/WHEEL_DIAMETER*ENCODER_TICKS * 1000 # TODO: calculate distance to encoder 
    # distance to encoder:
    Lfinal = Linit + encticks
    Rfinal = Rinit + encticks

    (Lprev, Rprev) = (Linit, Rinit)
    while 1:
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()
        # if we have traveled distance, stop.
        if(Lcurr > Lfinal or Rcurr > Rfinal):
            a_star.motors(0, 0)
            break
        # calculate errors (leaning left)
        err = (Lcurr - Lprev) - (Rcurr - Rprev)
        errsum += err
        errsig = Kp * err + Ki * errsum

        print("{:.2f}".format(errsig))
        # write to motor
        motorL = 100 - errsig
        motorR = 100 + errsig
        a_star.motors(int(motorL), int(motorR))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.1)

drive_straight(a_star, 1)