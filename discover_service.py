#!/usr/bin/env /usr/bin/python3
# discover_service.py [port]

import socket
import sys

DEFAULT_PORT = 5000 # The same port as used by the server

MAGIC = "fna349fn" # to make sure we don't confuse or get confused by other programs

from socket import socket, AF_INET, SOCK_DGRAM

def run(port):
    with socket(AF_INET, SOCK_DGRAM) as s:  #create UDP socket as s:
        s.bind(('', port))
        
        data, addr = s.recvfrom(1024) #wait for a packet
        if str(data, 'utf-8').startswith(MAGIC):
            print('Announcement: {} from {}'.format(str(data[len(MAGIC):], 'utf8'), addr[0]))
            return

if __name__ == "__main__":
    try:
        server_port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    except:
        print("Invalid port {}! Using default({})".format(sys.argv[1], DEFAULT_PORT))
        server_port = DEFAULT_PORT

    run(server_port)
