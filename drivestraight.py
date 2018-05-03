from a_star import AStar
import time

a_star = AStar()

Lenc = a_star.read_encoders()[0]
Renc = a_star.read_encoders()[1]

start = time.time()
end = start + 10

Kp = .0001
L, R = 100, 100
a_star.motors(L, R)


while 1:
    if (time.time() > end):
        a_star.motors(0, 0)
        break
    E = a_star.read_encoders()
    err = E[0] - E[1]
    err = Kp*err
    L -= err
    R += err
    a_star.motors(int(L), int(R))
    time.sleep(0.05)