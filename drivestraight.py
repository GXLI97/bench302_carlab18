from a_star import AStar
import time

a_star = AStar()

Lenc = a_star.read_encoders()[0]
Renc = a_star.read_encoders()[1]

start = time.time()
end = start + 10

Kp = .1
L, R = 100, 100
a_star.motors(L, R)


while 1:
    E = a_star.read_encoders()
    err = E[0] - E[1]
    err = K*err
    L -= err
    R += err
    a_star.motors()
