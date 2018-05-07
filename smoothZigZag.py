import time
import math
import sys
import serial
from a_star import AStar
from statistics import mean, median
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

def shutdown(ser, a_star):
    ser.write(b'lec\r')
    ser.close()
    a_star.motors(0, 0)

def calc_angle(di, dr, dl, df):
    x = di - df
    y = dl - dr
    return math.degrees(math.atan2(y, x)) + 30 # why +50?

def recordDistances(ser):
	distances = []
	i=0
	while 1:
		try:
			res = ser.readline()
			dist = parseDistance(res.decode('utf-8'))
			distances.append(dist)
			i+=1
		except:
			print("Read'n Parse failed")
			break
	m = mean(distances)
    print("Mean distance over {} measurements: {}".format(NUM_DISTANCES, m))
    return m

def smoothZigZag(ser, a_star):

	while 1:
		arcdrive(a_star, 1./4, leftTurn=1)

		print(recordDistances(ser))

		arcdrive(a_star, 1./4, leftTurn=-1)

		print(recordDistances(ser))

def main():
    DEBUG = True
    # initialize our AStar motor controller.
    a_star = AStar()
    ser = connect_to_serial()

    smoothZigZag(ser, a_star)

    shutdown(ser, a_star)

if __name__ == '__main__':
    main()





