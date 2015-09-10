import socket

target_host = '127.0.0.1'
target_port = 9999

# Creates a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the client
client.connect((target_host, target_port))

# Send some data
client.send('SEND!')

# Receive the response
response = client.recv(4096)

print response