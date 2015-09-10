import sys, socket, getopt, threading, subprocess

#----- global variables -----#
listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
port                = 0

def usage():
    print """
miniNC Net Tool

Usage: mini_nc.py -t [target_host] -p [port]
-l --listen                 - listen on [host]:[port] for incoming connections
-e --execute=[file_to_run]  - execute the given file upon receiving a connection
-c --command                - initialize a command shell
-u --upload=[destination]   - upon receiving connection upload file and write to destination

Examples:
mini_nc.py -t 192.168.1.1 -p 5555 -l -c
mini_nc.py -t 192.168.1.1 -p 5555 -l -u=C:\\target.exe
mini_nc.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\"
echo "ABCDEFGH" | .\mini_nc.py -t 192.168.11.12 -p 135
"""
    sys.exit(0)

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the target host
        client.connect((target, port))
         
        # If there is data to send, send it  
        if len(buffer):
            client.send(buffer)
        
        # Wait for data back
        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            # Wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # Send it off
            client.send(buffer)

    except:
        print "[*] Exception! Exiting..."
        
        # Bring the connection down
        client.close()

def client_handler(client_socket):
    global upload
    global execute
    global command

    # Check for upload
    if len(upload_destination):
        # Read all the bytes and write to out destination
        file_buffer = ""
        
        # Keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # Now take the bytes and try to write out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Acknowledge successful file write
            client_socket.send("Successfully saved the file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save the file to %s\r\n" % upload_destination)

    # Check for command execution
    if len(execute):
        # Run the command
        output = run_command(execute)
        client_socket.send(output)

    # If command shell was requested, go into loop
    if command:
        while True:
            # Show a simple prompt
            client_socket.send("<mNC:#> ")

            cmd_buffer = ""

            # Now receive until we see a linefeed (enter key)  
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Send back the command output
            response = run_command(cmd_buffer)
            client_socket.send(response)


def server_loop():
    global target

    # If no target is defined, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    # Trim the newline
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    # Send the output back to the client
    return output

def main():
    # Use previously defined global variables in this function
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # If no arguments were given, show usage
    if not len(sys.argv[1:]):
        usage()
    
    # Try to read the command line options, show usage if parameters dont match criteria
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    
    # Set variables based on arguments given
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-l", "--listen"):
            listen = True
        elif opt in ("-e", "--execute"):
            execute = arg
        elif opt in ("-c", "--commandshell"):
            command = True
        elif opt in ("-u", "--upload"):
            upload_destination = arg
        elif opt in ("-t", "--target"):
            target = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        else:
            assert False, "Unhandled Option!"

    # Listen or send data from stdin?
    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()   # <---Read in the buffer from the commandline. This will block, so send CTRL-D if not sending input to stdin
        client_sender(buffer)       # <---Send data off via client_sender function

    if listen:
        server_loop()

main()