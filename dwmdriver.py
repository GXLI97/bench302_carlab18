import serial
import time
import random
from a_star import AStar

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
	return math.sqrt(point[1]**2 + point[2]**2)

def stop(a_star):
	a_star.motors(0, 0)
	time.sleep(1)

def drive(a_star, delta):
	K = 20
	a_star.motors(100 + K*delta[0], 100 + K*delta[1])
	time.sleep(1)

def main():
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


	TARGETDISTANCE 	= 1
	TIMEOUT 		= 10

	# A = np.zeros(2) # the target of the bot
	xt = (0,0) # define start point of the bot at origin
	speed = 1
	direction = (1,0) # define starting direction as along the x-axis

	x1 = []
	x2 = []
	directions = []
	errs = []

	a_star.motors(100,100)
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
			print("Distance: {}".format(dist))
		except:
			print("Read'n Parse failed")
			continue

		errs.append(abs(TARGETDISTANCE - dist))
		if len(errs) < 2:
			continue

		directions.append(direction)
		if errs[-2] - errs[-1] > 0:
			sgn = 1
		else:
			sgn = -1

		if len(directions) > 2:
			direction = sgn * (directions[-1] - directions[-2])

		delta = (direction[0] - directions[-1][0],direction[1] - directions[-1][1])


		dist2 = distance(direction)
		direction = (direction[0] / dist2, direction[1] / dist2)

		stop(a_star)
		
		drive(a_star, delta)



