import socket
import select
import sys
import pickle
import random, string
import base64
import six
from thread import *

"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print "Invalid Command"
    print "Format: server <HOST IP> <PORT NUMBER>"
    exit()

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
keys = {}


server.bind((IP_address, Port))
server.listen(100)

list_of_clients = []


print("server started")

def newkey():
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    return x

def encode(string, key):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    encoded_string = encoded_string.encode('latin') if six.PY3 else encoded_string
    return base64.urlsafe_b64encode(encoded_string).rstrip(b'=')

def decode(string, key):
    string = base64.urlsafe_b64decode(string + b'===')
    string = string.decode('latin') if six.PY3 else string
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def clientthread(conn, addr):
    welcomeMessage = pickle.dumps(["Welcome to this chatroom!",keys[conn]], pickle.HIGHEST_PROTOCOL)
    conn.send(encode(welcomeMessage,"empty"))

    while True:
        try:
            message = conn.recv(2048)
            if message:
                deserialized_message = pickle.loads(decode(message, keys[conn]))
                name,message = deserialized_message
                # Print message on server terminal
                print "<" + name + "(" + addr[0] + ")> " + message

                # Calls broadcast function to send message to all
                message_to_send = "<" + name + "> " + message
                broadcast(message_to_send, conn)

            else:
                # if broken message, remove it
                remove(conn)

        except:
            continue

def broadcast(message, connection):
    for clients in list_of_clients:
        try:
            clients.send(encode(message,keys[clients]))
        except:
            clients.close()

            remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    keys[conn] = newkey()

    # prints the address of the user that just connected
    print addr[0] + " connected"

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread, (conn, addr))

conn.close()
server.close()
