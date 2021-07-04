import socket

#####CONNECTION#######
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER = '200.14.84.235'
PORT = 5000
print(f'starting up on {SERVER} port {PORT}')
socket.connect((SERVER, PORT))
####################

