from a_star import AStar
import time

a_star = AStar()

a_star.motors(25, -25)

start = time.time()
end=start+2

while 1:
    if time.time()>end:
        a_star.motors(0, 0)
        break
    print(a_star.read_encoders())
    time.sleep(0.1)
