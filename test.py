from a_star import AStar
import time

a_star = AStar()

L = a_star.read_encoders()[0]
R = a_star.read_encoders()[1]

a_star.motors(25, -25)

def calcEncodersRight():
    return (300, 300)

while 1:
    l90, r90 = calcEncodersRight()
    E = a_star.read_encoders()
    if (E[0]-L > l90 && E[1]-R > r90)
    print(E)
    time.sleep(0.05)
