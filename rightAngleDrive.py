import serial
import time
import random
import math
import sys
from a_star import AStar
from statistics import mean, median

def turn(a_star, degrees):
	BOTDIAM = 149.
	WHEELDIAM = 70.
	ENCODERTICKS = 1440.


	ticks = BOTDIAM * degrees * ENCODERTICKS / 360.0 / WHEELDIAM

	l = a_star.read_encoders()[0]
	r = a_star.read_encoders()[1]

	a_star.motors(25, -25)
	while 1:
		e = a_star.read_encoders()
		if abs(e[1]-r) + abs(e[0]-l) > 2 * ticks:
			a_star.motors(0, 0)
			return
		time.sleep(0.05)

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
	return ser

def parseDistance(s):
	a = s.strip().split(',')
	# print(a)
	return float(a[-1])

def main():
	global MAXMOTOR, MINMOTOR, TARGETDISTANCE, TIMEOUT, LSTRAIGHT, RSTRAIGHT, DRIVETIME, STOPTIME, KP, KD

	MAXMOTOR		= 200
	MINMOTOR		= 20
	TARGETDISTANCE 	= 1
	TIMEOUT 		= 60
	LSTRAIGHT 		= 110
	RSTRAIGHT 		= 100
	DRIVETIME 		= 3
	STOPTIME		= 1
	KP 				= 15
	KD				= 0

	
	# initialize our AStar motor controller.
	a_star = AStar()

	ser = connect_to_serial()
	time.sleep(1)
	ser.write(b'\r\r') # go into serial mode.
	time.sleep(2)
	res=ser.read(100) # read some things.
	time.sleep(0.5)
	time.sleep(0.5)
	timeout = time.time() + TIMEOUT
	ser.write(b'lec\r') # start writing distances.

	# Get distance at point B
	distances = []
	counter = 0
	while counter < 10:
		try:
			res = ser.readline()
			distances.append(parseDistance(res.decode('utf-8')))
			counter += 1
			# print("Distance: {}".format(dist))
		except:
			print("Read'n Parse failed")
			counter += 0.01
			continue
	distance = median(distances)
	print("B Distance: {}".format(distance))
	
	driveStraight()

	# Get distance at point A
	distances = []
	counter = 0
	while counter < 10:
		try:
			res = ser.readline()
			distances.append(parseDistance(res.decode('utf-8')))
			counter += 1
			# print("Distance: {}".format(dist))
		except:
			print("Read'n Parse failed")
			counter += 0.01
			continue
	distance = median(distances)
	print("A Distance: {}".format(distance))
	
	turn(a_star, 90)
	driveStraight()
	
	# Get distance at point C
	distances = []
	counter = 0
	while counter < 10:
		try:
			res = ser.readline()
			distances.append(parseDistance(res.decode('utf-8')))
			counter += 1
			# print("Distance: {}".format(dist))
		except:
			print("Read'n Parse failed")
			counter += 0.01
			continue
	distance = median(distances)
	print("C Distance: {}".format(distance))




if __name__ == '__main__':
	main()
