import socket
 
host = '10.9.67.44' 
port = 50008
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Connected to "+(host)+" on port "+str(port))
initialMessage = raw_input("Send: ")
s.sendall(initialMessage)
 
while True:
	data = s.recv(1024)
	print("Recieved: "+(data))
	response = raw_input("Reply: ")
	if response == "exit":
		break
	s.sendall(response)
s.close()