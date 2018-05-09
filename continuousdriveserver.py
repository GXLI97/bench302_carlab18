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

def read_distances(q, conn):
    while True:
        data = conn.recv(1024).decode()
        # print('Received {}'.format(data))
        data_arr = data.split(',')
        for i in range(len(data_arr) - 1):
            q.put_nowait(float(data_arr[i]))
    


def shutdown(a_star, p, conn):
    p.terminate()
    a_star.motors(0, 0)
    conn.close()

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
        
        

        if len(dist_data) > 0 and min(dist_data) < 1:
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
    host = '10.9.67.44' 
    port = 50008

    a_star = AStar()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    print ("Connection from", addr)

    q = Queue()
    p = Process(target=read_distances, args=(q, conn))
    p.start()

    try:
        meander(a_star, q)
        shutdown(a_star, p, conn)
    except (ErrorNumber, ErrorMessage):
        print(ErrorMessage)
        shutdown(a_star, p, conn)



if __name__ == '__main__':
    main()
