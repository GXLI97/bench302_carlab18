from multiprocessing import Process, Queue
import serial
import time
import random
import math
import sys
from a_star import AStar
from statistics import mean, median
from drivestraight import drive_straight
from arcdrive import arcdrive
from turn import turn
import numpy as np
import socket
# from arcdrive import arcdrive

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

def read_distances(ser, q, s):
    i = 0
    while 1:
        try:
            res = ser.readline()
            dist = parseDistance(res.decode('utf-8'))
            if not s is None:
                s.sendall(str(dist).encode('utf-8'))
            # print("Distance: {:.2f}".format(dist))
            q.put_nowait(dist)
            i += 1
        except:
            print("Read'n Parse failed")
            continue
    


def shutdown(ser, a_star, p, s):
    ser.write(b'lec\r')
    ser.close()
    p.terminate()
    a_star.motors(0, 0)
    if not s is None:
        s.close()

def arcdrive(a_star, radius, leftTurn=1, arc=180, speed=1.5):
    BOTDIAM = 149.
    WHEELDIAM = 70.
    ENCODERTICKS = 1440.
    OVERFLOW_BUFF = 65536
    Kp = 20
    Ki = 0.15

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
        time.sleep(0.005)

def meander(a_star, q):
    SPEED = 1.75
    
    Kp = 50
    Ki = 10
    Kd = 5

    # should fix this later.
    larc = 180
    rarc = 180

    r = 0
    r_sum = 0
    r_prev = 0

    while 1:
        arcdrive(a_star, radius=0.25, arc=larc, speed=SPEED)
        arcdrive(a_star, radius=0.25, arc=rarc, speed=SPEED, leftTurn=-1)
        print("\n================")
        print("Getting Data")
        dist_data = []
        while not q.empty():
            print(".", end="")
            dist_datum = q.get()
            dist_data.append(dist_datum)

        print("")
        
        

        if min(dist_data) < 1:
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
        if r > 0.7:
            r = 1
        elif r < -0.7:
            r = -1
        else:
            r = 0

        r_sum += r
        r_diff = r - r_prev 
        r_prev = r
        print("Errors: r={:.2f}, r_sum={:.2f}, r_diff={:.2f}".format(r, r_sum, r_diff))
        theta = Kp * r + Ki * r_sum + Kd * r_diff

        # if we are going directly away
        if m > .02/1.5*SPEED:
            theta = 180

        print("Theta calculation: {:.3f}".format(theta))

        if theta > 10:
            print("left turn")
            # a_star.motors(0,0)
            # time.sleep(1)
            # turn(a_star, theta, clockwise=-1)
            arcdrive(a_star, radius=0.25, arc=theta, speed=SPEED)
            # a_star.motors(0,0)
            # time.sleep(1)
        elif theta < -10:
            print("right turn")
            # a_star.motors(0,0)
            # time.sleep(1)
            # turn(a_star, theta, clockwise=1)
            arcdrive(a_star, radius=0.25, arc=-theta, speed=SPEED, leftTurn=-1)
            # a_star.motors(0,0)
            # time.sleep(1)
        else:
            print("straight")
            # a_star.motors(0,0)
            # time.sleep(1)
        
        print("Emptying queue")
        while not q.empty():
                dist_datum = q.get()
                if dist_datum < 1:
                    break
        # a_star.motors(0,0)
        # time.sleep(0.05)

        
def main():
    SOCKET = False
    if len(sys.argv) > 1:
        SOCKET = True

    a_star = AStar()

    ser = connect_to_serial()

    if SOCKET:
        host = '10.9.67.44' 
        port = 50008
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    else:
        s = None

    q = Queue()
    p = Process(target=read_distances, args=(ser, q, s))
    p.start()

    try:
        meander(a_star, q)
        shutdown(ser, a_star, p, s)
    except (ErrorNumber, ErrorMessage):
        print(ErrorMessage)
        shutdown(ser, a_star, p, s)



if __name__ == '__main__':
    main()
