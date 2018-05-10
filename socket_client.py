import socket
 
host = '10.9.229.181' 
port = 50008
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Connected to {} on port {}".format(host, port))
initialMessage = input("Send: ")
s.sendall(initialMessage.encode('utf-8'))
 
while True:
	data = s.recv(1024)
	print("Received: {}".format(int(data.decode()))
	response = input("Reply: ")
	if response == "exit":
		break
	s.sendall(response.encode('utf-8'))
s.close()