import socket
import select
import Queue
import sys

def server(port):
    server_socket = socket.socket()
    server_socket.bind(('localhost', port))
    server_socket.listen(5)
    return server_socket

sock = server(int(sys.argv[1]))
while(True):
    (new, addr) = sock.accept()
    temp = ""
    msg = new.recv(1024)
    while msg:
        temp += msg
        msg = new.recv(1024)
    print(temp)