import socket

targetHost = '127.0.0.1'
targetPort = 80

# Create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send some data
client.sendto('AAABBBCCC', (targetHost, targetPort))

# Receive some data
data, addr = client.recvfrom(4096)

print data