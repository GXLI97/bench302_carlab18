import serial
import time
import random
from a_star import AStar

TARGETDISTANCE = 1 #meter, I think
MAXMOTOR = 100
MINMOTOR = 0
TIMEOUT = 10

def parseDistance(s):
	a = s.strip().split(',')
	print(a)
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
	print(res.decode("utf-8"), end='', flush=True)
	time.sleep(0.5)
	time.sleep(0.5)
	timeout = time.time() + TIMEOUT
	ser.write(b'lec\r') # start writing distances.

	prevErr = 0
	err = 0
	while True:
		# in the future, we probably want this timeout to be much longer
		if time.time() > timeout:
			ser.write(b'lec\r')
			ser.close()
			break
		res=ser.readline()
		if len(res) <= 0:
			continue
		s = res.decode('utf-8')
		try:
			distance = parseDistance(s)
			print(distance)
		except:
			continue
		err = distance - TARGETDISTANCE

		# if the error is increasing, turn a different way
		if err > prevErr:
			turn(a_star)
		# otherwise, go straight
		else:
			drive(a_star, err, prevErr)
		# maybe in the future, turn() and drive() could be the same function

		prevErr = err

if __name__ == '__main__':
	main()
