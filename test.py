from a_star import AStar
import time

a_star = AStar()

while 1:
    left, right = map(int, input().split())
    a_star.motors(left, right)
    print(a_star.read_encoders())
