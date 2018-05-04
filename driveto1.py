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
    NUM_DISTANCES = 10
    distances = []
    while len(distances) < 10:
        try:
            res = ser.readline()
            dist = parseDistance(res.decode('utf-8'))
            distances.append(dist)
        except:
            print("Read'n Parse failed")
            continue
    return mean(distances)


def main():
    TIMEOUT = 60

    # initialize our AStar motor controller.
    a_star = AStar()

    ser = connect_to_serial()

    d1 = record_distance(ser)
    drive_straight(a_star, dist=1)
    d2 = record_distance(ser)
    turn(a_star, degrees=90, clockwise=1)
    drive_straight(a_star, dist=1)
    d3 = record_distance(ser)

    print("Distances {:.2f} {:.2f} {:.2f}".format(d1, d2, d3))
    # record distance.

if __name__ == '__main__':
    main()





