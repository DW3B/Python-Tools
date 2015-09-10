import socket
import threading

bindIP = '0.0.0.0'
bindPort = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bindIP, bindPort))
server.listen(5)

print '[*] Listening on %s:%d' % (bindIP, bindPort)

# This is our client-handling thread
def HandleClient(clientSocket):
    # Print out what the client sends
    request = clientSocket.recv(1024)

    print '[*] Received: %s' % request

    # Send back a packet
    clientSocket.send('ACK!')
    clientSocket.close()

while True:
    client, addr = server.accept()
    
    print '[*] Accepted connection from: %s:%d' % (addr[0], addr[1])

    # Spin up the client thread to handle incoming data
    clientHandler = threading.Thread(target=HandleClient, args=(client,))
    clientHandler.start()
