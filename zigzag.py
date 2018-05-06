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

def parseDistance(s, ID="0C25"):

    # DIST,2,AN0,820C,0.00,0.00,0.00,7.24,AN1,0C25,0.00,0.00,0.00,2.55
    a = s.strip().split(',')
    k = 0
    while not a[-6*k -5] == ID:
        k += 1
    # print(a)
    return float(a[-6*k -1])

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
            # print("Distance: {:.2f}".format(dist))
            distances.append(dist)
        except:
            print("Read'n Parse failed")
            continue
    m = mean(distances)
    print("Mean distance over {} measurements: {}".format(NUM_DISTANCES, m))
    return m

def shutdown(ser, a_star):
    ser.write(b'lec\r')
    ser.close()
    a_star.motors(0, 0)

def zigzag(ser, a_star, stride, DEBUG=False):
    # d1 = record_distance(ser)
    # time.sleep(0.25)
    # turn(a_star, 45, DEBUG=DEBUG)
    # time.sleep(0.25)
    # drive_straight(a_star, stride, DEBUG=DEBUG)
    # print("========================")

    # d2 = record_distance(ser)
    # time.sleep(0.25)
    # turn(a_star, -90, DEBUG=DEBUG)
    # time.sleep(0.25)
    # drive_straight(a_star, 2*stride, DEBUG=DEBUG)
    # print("========================")

    # d3 = record_distance(ser)
    # time.sleep(0.25)
    # turn(a_star, 90, DEBUG=DEBUG)
    # time.sleep(0.25)
    # drive_straight(a_star, stride, DEBUG=DEBUG)
    # time.sleep(0.25)
    # turn(a_star, -45, DEBUG=DEBUG)
    # print("========================")

    # d4 = record_distance(ser)
    # time.sleep(0.25)
    # print("========================")
    # print("Distances: {:.2f} {:2f} {:2f} {:2f}".format(d1, d2, d3, d4))

    # return d1, d2, d3, d4

    # Attempt to reorder statements to reduce waiting time
    time.sleep(0.1)
    turn(a_star, 45, DEBUG=DEBUG)
    d1 = record_distance(ser)
    time.sleep(0.1)
    drive_straight(a_star, stride, DEBUG=DEBUG)
    print("========================")

    
    time.sleep(0.1)
    turn(a_star, -90, DEBUG=DEBUG)
    d2 = record_distance(ser)
    time.sleep(0.1)
    drive_straight(a_star, 2*stride, DEBUG=DEBUG)
    print("========================")

    time.sleep(0.1)
    turn(a_star, 90, DEBUG=DEBUG)
    d3 = record_distance(ser)
    time.sleep(0.1)
    drive_straight(a_star, stride, DEBUG=DEBUG)
    d4 = record_distance(ser)
    time.sleep(0.1)
    turn(a_star, -45, DEBUG=DEBUG)

    print("========================")
    print("Distances: {:.2f} {:2f} {:2f} {:2f}".format(d1, d2, d3, d4))

    return d1, d2, d3, d4

# TODO: make this more accurate.
def calc_angle(di, dr, dl, df):
    x = di - df
    y = dl - dr
    return math.degrees(math.atan2(y, x)) + 50

def zag(ser, a_star, DEBUG=False):
    # do stuff.
    di = record_distance(ser)
    d1, d2, d3, d4 = zigzag(ser, a_star, stride=0.25, DEBUG=DEBUG)
    while d4 > 1 and d3 > 1 and d2 > 1 and d1 > 1:
        angle = calc_angle(d1, d2, d3, d4)
        print("==================")
        print("angle: {:.2f}".format(angle))
        time.sleep(0.1)
        turn(a_star, angle, DEBUG=DEBUG)
        time.sleep(0.1)
        drive_straight(a_star, 0.25, DEBUG=DEBUG)
        d1, d2, d3, d4 = zigzag(ser, a_star, stride=0.25, DEBUG=DEBUG)

def main():
    DEBUG = True
    # initialize our AStar motor controller.
    a_star = AStar()
    ser = connect_to_serial()

    zag(ser, a_star, DEBUG)

    shutdown(ser, a_star)

if __name__ == '__main__':
    main()





