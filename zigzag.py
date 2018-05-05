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
    time.sleep(0.5)
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
    return mean(distances)

def shutdown(ser, a_star):
    ser.write(b'lec\r')
    ser.close()
    a_star.motors(0, 0)

def zigzag(ser, a_star, stride):
    d1 = record_distance(ser)
    time.sleep(0.5)
    turn(a_star, 45)
    time.sleep(0.5)
    drive_straight(a_star, stride)
    print("========================")

    d2 = record_distance(ser)
    time.sleep(0.5)
    turn(a_star, -80)
    time.sleep(0.5)
    drive_straight(a_star, 2*stride)
    print("========================")

    d3 = record_distance(ser)
    time.sleep(0.5)
    turn(a_star, 90)
    time.sleep(0.5)
    drive_straight(a_star, stride)
    time.sleep(0.5)
    turn(a_star, -40)
    print("========================")

    d4 = record_distance(ser)
    time.sleep(0.5)
    print("========================")
    print("Distances: {:.2f} {:2f} {:2f} {:2f}".format(d1, d2, d3, d4))

    return d1, d2, d3, d4

def calc_angle(di, dr, dl, df):
    x = di-df
    el = dl - (di+3*df)/4
    er = dr - (3*di+df)/4
    y = er - el

    print("error left: {:.2f}".format(el))
    print("error right: {:.2f}".format(er))
    print("x: {:.2f}, y: {:.2f}".format(x,y))
    phi = math.degrees(math.atan2(1.25*y, x))
    return phi

def zag(ser, a_star):
    # do stuff.
    d4 = 100
    while d4 > 1:
        d1, d2, d3, d4 = zigzag(ser, a_star, stride=0.25)
        angle = calc_angle(d1, d2, d3, d4)
        print("==================")
        print("angle: {:.2f}".format(angle))
        turn(a_star, angle)
        time.sleep(0.5)
        drive_straight(a_star, d4*0.25)

def main():
    TIMEOUT = 60

    # initialize our AStar motor controller.
    a_star = AStar()
    ser = connect_to_serial()

    zag(ser, a_star)

    shutdown(ser, a_star)

if __name__ == '__main__':
    main()





