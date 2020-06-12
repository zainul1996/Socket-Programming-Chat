import socket
import select
import sys
import pickle
import base64
import six

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
key = "empty";
# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print "Invalid Command"
    print "Format: server <HOST IP> <PORT NUMBER>"
    exit()

name = raw_input("Input Username: ")

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

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

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]
    read_sockets, write_socket, error_socket = select.select(
        sockets_list, [], [])
    for socks in read_sockets:
        # From server
        if socks == server:
            message = socks.recv(2048)
            if key is "empty":
                welcomeMessage,key = pickle.loads(decode(message,key))
                message = welcomeMessage
            else:
                welcomeMessage = decode(message,key)
                message = welcomeMessage

            print message
        else:
            #From me
            message = sys.stdin.readline()
            # sys.stdout.write("\033[F") #back to previous line
            # sys.stdout.write("\033[K") #clear line
            message_to_send = pickle.dumps([name,message], pickle.HIGHEST_PROTOCOL)
            server.send(encode(message_to_send,key))
            # sys.stdout.write(bcolors.OKBLUE + "<You>" + bcolors.ENDC)
            # sys.stdout.write(message+"\n")
            sys.stdout.flush()
server.close()
