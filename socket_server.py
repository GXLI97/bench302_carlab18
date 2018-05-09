import socket
import time

host = '10.9.67.44'
port = 50008

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
conn, addr = s.accept()
print ("Connection from", addr)
while True:
    data = conn.recv(1024)
    if not data: break
    print("Received: "+(data.decode()))
    # response = input("Reply: ")
    # if response == "exit":
    #     break
    # conn.sendall(response.encode())
conn.close()