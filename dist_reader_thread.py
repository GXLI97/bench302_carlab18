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
            q.put([dist])
            i += 1
        except:
            print("Read'n Parse failed")
            continue

def main():
    ser = connect_to_serial()
    # begin to read distances in a thread.
    q = Queue()
    p = Process(target=read_distances, args=(ser, q))
    p.start()
    time.sleep(5)
    while not q.empty():
        print(q.get())



if __name__ == '__main__':
    main()
