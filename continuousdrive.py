from multiprocessing import Process, Queue
import serial
import time
import random
import math
import sys
from a_star import AStar
from statistics import mean, median
from drivestraight import drive_straight
from turn import turn
import numpy as np
from arcdrive import arcdrive

def connect_to_serial():
    try:
        ser = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        timeout=0.5
        )
        print("connected successfully!")
    except:
        ser = serial.Serial(
        port='/dev/ttyACM1',
        baudrate=115200,
        timeout=0.5
        )

    time.sleep(1)
    ser.write(b'\r\r') # go into serial mode.
    time.sleep(2)
    res=ser.read(100) # read some things.
    time.sleep(0.5)
    time.sleep(0.5)
    ser.write(b'lec\r') # start writing distances.
    return ser

def parseDistance(s, ID="0C25"):

    # DIST,2,AN0,820C,0.00,0.00,0.00,7.24,AN1,0C25,0.00,0.00,0.00,2.55
    a = s.strip().split(',')
    k = 0
    while not a[-6*k -5] == ID:
        k += 1
    # print(a)
    return float(a[-6*k -1])

def read_distances(ser, q):
    i = 0
    while 1:
        try:
            res = ser.readline()
            dist = parseDistance(res.decode('utf-8'))
            # print("Distance: {:.2f}".format(dist))
            q.put_nowait(dist)
            i += 1
        except:
            print("Read'n Parse failed")
            continue

def shutdown(ser, a_star):
    ser.write(b'lec\r')
    ser.close()
    a_star.motors(0, 0)

def arcdrive(a_star, radius, leftTurn=1, arc=180, speed=1):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536
    Kp = 1.5
    Ki = 0.01

    errsum = 0

    # get the initial encoder reading:
    (Linit, Rinit) = a_star.read_encoders()

    (Lprev, Rprev) = (Linit, Rinit)

    Lfinal = Linit + (1000*radius - leftTurn*BOTDIAM/2)/WHEELDIAM*ENCODERTICKS*(arc/180.)
    Rfinal = Rinit + (1000*radius + leftTurn*BOTDIAM/2)/WHEELDIAM*ENCODERTICKS*(arc/180.)
    #print("Linit: {}\tLfinal: {}\tRinit: {}\tRfinal: {}".format(Linit, Lfinal, Rinit,Rfinal))

    (Lprev, Rprev) = (Linit, Rinit)
    while 1:
        
        # get encoder reading
        (Lcurr, Rcurr) = a_star.read_encoders()

        if (Lcurr > Lfinal or Rcurr > Rfinal):
            #print("Lcurr: {}\tLfinal: {}\tRcurr: {}\tRfinal: {}".format(Lcurr, Lfinal, Rcurr, Rfinal))
            a_star.motors(int(speed*105), int(speed*100))
            break

        # calculate errors (leaning left)
        # missing logic here to actually make the turn
        err = ((Lcurr - Lprev + OVERFLOW_BUFF) % OVERFLOW_BUFF)*(1000*radius + leftTurn*BOTDIAM/2)/(1000*radius) - ((Rcurr - Rprev + OVERFLOW_BUFF) % OVERFLOW_BUFF)*(1000*radius - leftTurn*BOTDIAM/2)/(1000*radius)
        errsum += err
        errsig = Kp * err + Ki * errsum
        # print("{:.2f}".format(errsig))
        # write to motor
        motorL = speed*105  - errsig
        motorR = speed*100  + errsig
        a_star.motors(int(motorL), int(motorR))
        # print("Motors on {} {}".format(int(motorL), int(motorR)))
        # update previous
        (Lprev, Rprev) = (Lcurr, Rcurr)
        time.sleep(0.05)

def meander(a_star, q):
    # begin to read distances in a thread.
    
    Kp = 30
    Ki = 15
    Kd = 0

    # should fix this later.
    larc = 180
    rarc = 200

    r = 0
    r_sum = 0

    # ideally dont need this.
    OFFSET = 0

    while 1:
        arcdrive(a_star, radius=0.25, arc=larc)
        arcdrive(a_star, radius=0.25, arc=rarc, leftTurn=-1)

        dist_data = []
        while not q.empty():
            dist_data.append(q.get_nowait())
        
        print("================")

        if mean(dist_data) < 1:
            break

        d = np.array(dist_data)
        x = np.linspace(1, len(dist_data)+1, len(dist_data))
        m,b = np.polyfit(x, dist_data, 1)
        line = m * x + b
        normalized = d - line

        sine = np.sin(2*math.pi / len(x) * x)

        r = np.dot(sine, normalized)
        print("Line slope: {:.3f}".format(m))
        print("R value: {:.3f}".format(r))

        # discretize R.
        if r > 1:
            r = 1
        elif r < -1:
            r = -1
        else:
            r = 0

        r_sum += r
        print("Errors: r={:.2f}, r_sum={:.2f}".format(r, r_sum))
        theta = OFFSET + Kp * r + Ki * r_sum

        print("Theta calculation: {:.3f}".format(theta))

        if theta > 10:
            print("left turn")
            # a_star.motors(0,0)
            # time.sleep(1)
            arcdrive(a_star, radius=0.25, arc=theta)
            # a_star.motors(0,0)
            # time.sleep(1)
            while not q.empty():
                q.get_nowait()
        elif theta < -10:
            print("right turn")
            # a_star.motors(0,0)
            # time.sleep(1)
            arcdrive(a_star, radius=0.25, arc=-theta, leftTurn=-1)
            # a_star.motors(0,0)
            # time.sleep(1)
            while not q.empty():
                q.get_nowait()
        else:
            print("straight\n")
            # a_star.motors(0,0)
            # time.sleep(1)
            while not q.empty():
                q.get_nowait()

        
def main():
    a_star = AStar()

    ser = connect_to_serial()

    q = Queue()
    p = Process(target=read_distances, args=(ser, q))
    p.start()


    meander(a_star, q)


    shutdown(ser, a_star)
    p.terminate()


if __name__ == '__main__':
    main()
