 import serial
import time
import random
import math
import sys
from a_star import AStar
from statistics import mean, median



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

def distance(point):
	return math.sqrt(point[1]**2 + point[0]**2)

def stop(a_star):
	a_star.motors(0, 0)
	time.sleep(STOPTIME)

def drive(a_star, delta, prevDelta):
	if prevDelta is None:
		prevDelta = delta

	l = LSTRAIGHT + KP*delta[0] + KD*(delta[0] - prevDelta[0])
	if l < MINMOTOR:
		l = MINMOTOR
	elif l > MAXMOTOR:
		l = MAXMOTOR

	r = LSTRAIGHT + KP * delta[1] + KD*(delta[1] - prevDelta[1])
	if r < MINMOTOR:
		r = MINMOTOR
	elif r > MAXMOTOR:
		r = MAXMOTOR

	a_star.motors(-1*int(l), -1*int(r))
	print("Motors on {}, {}".format(l, r))
	time.sleep(DRIVETIME)

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
	KD				= 1

	if len(sys.argv) == 4:
		DRIVETIME = float(sys.argv[1])
		KP = float(sys.argv[2])
		KD = float(sys.argv[3])
	
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


	

	# A = np.zeros(2) # the target of the bot
	xt = (0,0) # define start point of the bot at origin
	speed = 1
	direction = (1,0) # define starting direction as along the x-axis

	x1 = []
	x2 = []
	directions = []
	errs = []
	distances = []

	a_star.motors(110,100)
	delta = None
	prevDelta = None
	i = 0
	while True:
		# in the future, we probably want this timeout to be much longer
		if time.time() > timeout:
			ser.write(b'lec\r')
			ser.close()
			a_star.motors(0, 0)
			break
		
		try:
			res = ser.readline()
			dist = parseDistance(res.decode('utf-8'))
			distances.append(dist)
			i += 1
			print("Distance: {}".format(dist))
		except:
			print("Read'n Parse failed")
			continue
		if (i%10) == 0:
			avg = median(distances[-10:])
			print("Averaged Distance: {:.2f}".format(avg))

			errs.append(abs(TARGETDISTANCE - avg))
			if len(errs) < 2:
				continue

			directions.append(direction)
			if errs[-2] - errs[-1] > 0:
				sgn = 1
			else:
				sgn = -1

			if len(directions) > 2:
				direction = (sgn * (directions[-1][0] - directions[-2][0]), sgn * (directions[-1][1] - directions[-2][1]))

			delta = (direction[0] - directions[-1][0], direction[1] - directions[-1][1])
			print("delta: {}".format(delta))

			dist2 = distance(direction) + random.uniform(-0.5, 0.5)
			direction = (direction[0] / dist2, direction[1] / dist2)

			stop(a_star)
			
			drive(a_star, delta, prevDelta)

			prevDelta = delta


if __name__ == '__main__':
	main()
