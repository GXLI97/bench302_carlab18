from a_star import AStar
import time

a_star = AStar()

L = a_star.read_encoders()[0]
R = a_star.read_encoders()[1]

a_star.motors(25, -25)

def calcEncodersRight():
    return (2407, 2407)

while 1:
    Eopt = calcEncodersRight()
    E = a_star.read_encoders()
    if (E[0]-L > Eopt[0] and E[1]-R > Eopt[1])
    print(E)
    time.sleep(0.05)
