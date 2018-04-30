import serial
import time
import random
from a_star import AStar

TARGETDISTANCE = 1 #meter, I think
MAXMOTOR = 400
MINMOTOR = 0
TIMEOUT = 10

def parseDistance(s):
	a = s.split(',')
	return float(a[len(a)])

# in the future, maybe use a better function than random
def turn(a_star):
	r = random.randInt(-MAXMOTOR/2, MAXMOTOR/2)
	a_star.motors(0, r)

# somehow need to map a changing error to a motor power
def drive(a_star, err, prevErr):
	d = (err - prevErr)*1.0 / TARGETDISTANCE
	l = MAXMOTOR * d
	r = MAXMOTOR * d
	a_star.motors(int(l), (r))

def main():
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

	a_star = AStar()

	time.sleep(1)
	ser.write(b'\r\r')
	time.sleep(2)
	res=ser.read(100)
	print(res.decode("utf-8"), end='', flush=True)
	time.sleep(0.5)

	time.sleep(0.5)
	timeout = time.time() + TIMEOUT

	ser.write(b'lec\r')

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
		print(s)
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
