import socket
import select
import sys
import utils

def client(name, ip, port):
    client_socket = socket.socket()

    # connect to remote host
    try:
        client_socket.connect((ip, port))
    except:
        sys.stdout.write(utils.CLIENT_CANNOT_CONNECT.format(ip, port) + '\n')
        sys.exit()

    client_socket.send(addPadding(name))
    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()

    temp = ""
    while True:
        allSockets = [sys.stdin, client_socket]

        # get the list sockets which are ready to be read through select
        to_read, to_write, error = select.select(allSockets, [], [])

        for sock in to_read:
            if sock == client_socket:
                data = sock.recv(utils.MESSAGE_LENGTH)
                if not data:
                    sys.stdout.write(utils.CLIENT_WIPE_ME + '\r' + utils.CLIENT_SERVER_DISCONNECTED.format(ip, port) + '\n')
                    sys.exit()
                else:
                    if len(data) < utils.MESSAGE_LENGTH:
                        if temp != "":
                            if len(temp) + len(data) >= utils.MESSAGE_LENGTH:
                                data = temp + data
                                temp = ""
                                sys.stdout.write(utils.CLIENT_WIPE_ME + '\r' + data.rstrip())
                            else:
                                temp = temp + data
                        else:
                            temp = data
                    else:
                        sys.stdout.write(utils.CLIENT_WIPE_ME + '\r' + data.rstrip() + '\n')
                    sys.stdout.write(utils.CLIENT_WIPE_ME + '\r' + utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()
            else:
                # user has entered a message
                msg = sys.stdin.readline()
                client_socket.sendall(addPadding(msg))
                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                sys.stdout.flush()

def addPadding(msg):
    length = len(msg)
    if length < utils.MESSAGE_LENGTH:
        for x in range(utils.MESSAGE_LENGTH - length):
            msg += ' '
    return msg

args = sys.argv
if len(args) != 4:
    sys.stdout.write("Please input your name, the host address, and port number")
    sys.exit()
client(args[1], args[2], int(args[3]))