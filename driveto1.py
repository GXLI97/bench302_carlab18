import serial
import time
import random
import math
import sys
from a_star import AStar
from statistics import mean, median
from drivestraight import drive_straight
from turn import turn

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

def parseDistance(s):
    a = s.strip().split(',')
    # print(a)
    return float(a[-1])

def record_distance(ser):
    time.sleep(1)
    ser.read(100000000)
    ser.read(100000000)
    NUM_DISTANCES = 20
    distances = []
    while len(distances) < NUM_DISTANCES:
        try:
            res = ser.readline()
            dist = parseDistance(res.decode('utf-8'))
            print("Distance: {:.2f}".format(dist))
            distances.append(dist)
        except:
            print("Read'n Parse failed")
            continue
    return median(distances)

def calc_angle(dist, d1, d2, d3):
    cosT1 = (dist**2 + d2**2 - d1**2)/(2*dist*d2)
    if cosT1 > 1:
        cosT1 = 1
    elif cosT1 < -1:
        cosT1 = -1
    cosT2 = (dist**2 + d2**2 - d3**2)/(2*dist*d2)
    if cosT2 > 1:
        cosT2 = 1
    elif cosT2 < -1:
        cosT2 = -1
    T1 = math.acos(cosT1)
    T2 = math.acos(cosT2)
    if cosT1 > 0 and cosT2 > 0:
        angle = mean([math.pi/2-T1, T2])
    elif cosT1 > 0 and cosT2 < 0:
        angle = mean([math.pi/2+T1, T2])
    elif cosT1 < 0 and cosT2 > 0:
        angle = mean([math.pi/2-T1, -T2])
    elif cosT1 < 0 and cosT2 < 0:
        angle = mean([T1-3*math.pi/2,-T2])
    return angle * 180/math.pi


def shutdown(ser, a_star):
    ser.write(b'lec\r')
    ser.close()
    a_star.motors(0, 0)

def move_step(ser, a_star, EVAL_DIST):
    d1 = record_distance(ser)
    drive_straight(a_star, dist=EVAL_DIST)
    d2 = record_distance(ser)
    turn(a_star, degrees=90, clockwise=1)
    time.sleep(0.5)
    drive_straight(a_star, dist=EVAL_DIST)
    d3 = record_distance(ser)

    print("Distances {:.2f} {:.2f} {:.2f}".format(d1, d2, d3))

    # go now to correct location:
    drive_straight(a_star, dist=EVAL_DIST, forward=-1)
    degrees = calc_angle(EVAL_DIST, d1, d2, d3)
    print("Calculated turn angle: {:.2f}".format(degrees))
    time.sleep(0.5)
    turn(a_star, degrees, clockwise=1)
    time.sleep(0.5)
    drive_straight(a_star, dist=d2 * 0.5)
    dend = record_distance(ser)
    return dend

def main():
    TIMEOUT = 60

    # initialize our AStar motor controller.
    a_star = AStar()
    ser = connect_to_serial()

    dend = 4.
    while dend > 1:
        dend = move_step(ser, a_star, dend/2)
        print("Distance after movement: {:.2f}".format(dend))
    shutdown(ser, a_star)

if __name__ == '__main__':
    main()





