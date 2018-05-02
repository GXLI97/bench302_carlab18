import serial
import time
import random
from a_star import AStar
from statistics import mean

TARGETDISTANCE = 1 #meter, I think
MAXMOTOR = 50
MINMOTOR = 0
TIMEOUT = 10

def parseDistance(s):
	a = s.strip().split(',')
	# print(a)
	return float(a[-1])

# in the future, maybe use a better function than random
def turn(a_star):
	r = random.randint(-MAXMOTOR/2, MAXMOTOR/2)
	print("Motor set to {} {}".format(0,r))
	a_star.motors(0, r)

# somehow need to map a changing error to a motor power
def drive(a_star, err, prevErr):
	d = (err - prevErr)*1.0 / TARGETDISTANCE
	l = MAXMOTOR * d
	r = MAXMOTOR * d
	a_star.motors(int(l), int(r))

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


def main():
	# initialize our AStar motor controller.
	a_star = AStar()

	ser = connect_to_serial()
	time.sleep(1)
	ser.write(b'\r\r') # go into serial mode.
	time.sleep(2)
	res=ser.read(100) # read some things.
	# print(res.decode("utf-8"), end='', flush=True)
	time.sleep(0.5)
	time.sleep(0.5)
	timeout = time.time() + TIMEOUT
	ser.write(b'lec\r') # start writing distances.

	errs = []
	distances = []
	l, r = 150, 150

	i = 0
	while True:
		i += 1
		# in the future, we probably want this timeout to be much longer
		if time.time() > timeout:
			ser.write(b'lec\r')
			ser.close()
			a_star.motors(0, 0)
			break
		res=ser.readline()
		if len(res) <= 0:
			continue
		s = res.decode('utf-8')
		try:
			dist = parseDistance(s)
			# print("Distance: {}".format(dist))
			distances.append(dist)
		except:
			print("uhoh")
			continue

		if (i%10)== 0:
			avg = mean(distances[-10:])
			print("Averaged Distance: {:.2f}".format(avg))
			errs.append(avg - TARGETDISTANCE)

			# do stuff.
			if len(errs) < 3:
				continue

			d1 = errs[-2] - errs[-1]
			d2 = errs[-3] - errs[-2]
			dd = d1-d2 

			print("Errors: d1 = {:.2f}, d2 = {:.2f}, dd = {:.2f}".format(d1,d2,dd))

			if d1 < 0.1:
				a_star.motors(150, 150)
				continue

			if dd < 0:
				# turn in same direction.
				shift = 10
				if l>=r:
					l += shift
					r -= shift
				else:
					l -= shift
					r += shift
				a_star.motors(l, r)
			else:
				# turn in opposite direction.
				shift = -10
				if l>=r:
					l += shift
					r -= shift
				else:
					l -= shift
					r += shift
				a_star.motors(l, r)

			print("Direction: {} {}".format(l, r))

if __name__ == '__main__':
	main()
