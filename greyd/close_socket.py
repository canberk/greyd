import socket
soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"
port = 8001
soket.connect((host, port))
soket.send("CloseServer".encode())
soket.close()
