from a_star import AStar
import time

a_star = AStar()

L = a_star.read_encoders()[0]
R = a_star.read_encoders()[1]

a_star.motors(25, -25)

def calcEncodersRight():
    return (2407, 2407)

Eopt = calcEncodersRight()
print(Eopt)

while 1:
    Eopt = calcEncodersRight()
    E = a_star.read_encoders()
    if (E[0]-L > Eopt[0] or E[1]-R > Eopt[1]):
        break
    print(E)
    time.sleep(0.05)
