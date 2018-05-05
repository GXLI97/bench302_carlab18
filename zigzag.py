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

def shutdown(ser, a_star):
    ser.write(b'lec\r')
    ser.close()
    a_star.motors(0, 0)

def zigzag(a_star, stride):
    time.sleep(0.5)
    turn(a_star, 45)
    time.sleep(0.5)
    drive_straight(a_star, stride)
    time.sleep(0.5)
    turn(a_star, -80)
    time.sleep(0.5)
    drive_straight(a_star, 2*stride)
    time.sleep(0.5)
    turn(a_star, 90)
    time.sleep(0.5)
    drive_straight(a_star, stride)
    time.sleep(0.5)
    turn(a_star, -40)
    time.sleep(0.5)


def main():
    TIMEOUT = 60

    # initialize our AStar motor controller.
    a_star = AStar()
    ser = connect_to_serial()

    # do stuff.
    zigzag(a_star, stride=0.5)
    shutdown(ser, a_star)

if __name__ == '__main__':
    main()





