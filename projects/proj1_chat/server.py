import socket
import select
import sys
import utils

allSockets = []
usernames = {}
rooms = {}
channels = {}

def server(port):

    server_socket = socket.socket()
    server_socket.bind(('', port))
    server_socket.listen(5)
 
    # add server socket object to the list of readable connections
    allSockets.append(server_socket)
    
    temp = ""
    while True:
        # get the list sockets which are ready to be read through select
        to_read, to_write, error = select.select(allSockets, [], [], 0)
      
        for sock in to_read:
            # a new connection request recieved
            if sock == server_socket: 
                (new_sock, addr) = server_socket.accept()
                allSockets.append(new_sock)
                name = new_sock.recv(utils.MESSAGE_LENGTH)
                # name should be checked within client so should exist
                if name:
                    if len(name) < utils.MESSAGE_LENGTH:
                        if temp != "":
                            if len(temp) + len(name) >= utils.MESSAGE_LENGTH:
                                name = temp + name
                                temp = name[utils.MESSAGE_LENGTH:]
                                usernames[new_sock] = name.rstrip()
                            else:
                                temp = temp + name
                        else:
                            temp = name
                    else:
                        usernames[new_sock] = name.rstrip()
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(utils.MESSAGE_LENGTH)
                    if data:
                        # if data is less than 200 bytes
                        if len(data) < utils.MESSAGE_LENGTH:
                            if temp != "":
                                if len(temp) + len(data) >= utils.MESSAGE_LENGTH:
                                    data = temp + data
                                    temp = data[utils.MESSAGE_LENGTH:]
                                    processData(sock, data.rstrip())
                                else:
                                    temp = temp + data
                            else:
                                temp = data
                        else:
                            processData(sock, data)
                    else:
                        # remove the socket that's broken    
                        if sock in allSockets:
                            allSockets.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcastRoom(rooms[sock], sock, utils.SERVER_CLIENT_LEFT_CHANNEL.format(usernames[sock]) + '\n')
                # exception 
                except:
                    if sock in rooms:
                        broadcastRoom(rooms[sock], sock, utils.SERVER_CLIENT_LEFT_CHANNEL.format(usernames[sock]) + '\n')

    server_socket.close()

def processData(sock, data):
    if data[0] == '/':
        input_msg = data.rstrip().split(' ', 1)
        # if room is not specified
        if input_msg[0] == '/join' and len(input_msg) == 1:
            sock.sendall(addPadding(utils.SERVER_JOIN_REQUIRES_ARGUMENT))
        elif input_msg[0] == '/create' and len(input_msg) == 1:
            sock.sendall(addPadding(utils.SERVER_CREATE_REQUIRES_ARGUMENT))
        elif input_msg[0] == '/list':
            for room in channels:
                sock.sendall(addPadding(utils.CLIENT_WIPE_ME + '\r' + room))
        elif input_msg[0] == '/join':
            room = input_msg[1]
            if room in channels:
                # if user is already in another room
                if sock in rooms:
                    broadcastRoom(rooms[sock], sock, utils.CLIENT_WIPE_ME + '\r' + utils.SERVER_CLIENT_LEFT_CHANNEL.format(usernames[sock]))
                    channels[rooms[sock]].remove(sock)
                # broadcast to everyone else in new room that user is joining
                # and join the new room
                if channels[room]:
                    channels[room].append(sock)
                else:
                    channels[room] = [sock]
                rooms[sock] = room
                broadcastRoom(room, sock, utils.SERVER_CLIENT_JOINED_CHANNEL.format(usernames[sock]) )
            else:
                # cannot join a non-existent room
                sock.sendall(addPadding(utils.SERVER_NO_CHANNEL_EXISTS.format(room)))
        elif input_msg[0] == '/create':
            if input_msg[1] in channels:
                # cannot create an existing room
                sock.sendall(addPadding(utils.SERVER_CHANNEL_EXISTS.format(room)))
            else:
                room = input_msg[1]
                # if user is already in a room
                if sock in rooms:
                    broadcastRoom(rooms[sock], sock, utils.SERVER_CLIENT_LEFT_CHANNEL.format(usernames[sock]))
                    channels[rooms[sock]].remove(sock)
                if room in channels:
                    channels[room].append(sock)
                else:
                    channels[room] = [sock]
                rooms[sock] = room
        else:
            sock.sendall(addPadding(utils.SERVER_INVALID_CONTROL_MESSAGE.format(input_msg[0])))
    else:
        if sock in rooms:
            broadcastRoom(rooms[sock], sock, '\r[' + usernames[sock] + '] ' + data)
        else:
            sock.sendall(addPadding(utils.SERVER_CLIENT_NOT_IN_CHANNEL))

def broadcastRoom(room, curr_sock, msg):
    for users in channels[room]:
        if users != curr_sock:
            try:
                users.sendall(addPadding(msg))
            except:
                # broken socket connection
                users.close()
                # broken socket, remove it
                if users in channels[room]:
                    channels[room].remove(users)
                if users in allSockets:
                    allSockets.remove(users)

def addPadding(msg):
    length = len(msg)
    if length < utils.MESSAGE_LENGTH:
        for x in range(utils.MESSAGE_LENGTH - length):
            msg += ' '
    return msg

args = sys.argv
if len(args) != 2:
    sys.stdout.write("Please input the port number")
    sys.exit()
server(int(args[1]))