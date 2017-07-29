#!/usr/bin/env /usr/bin/python3
# dclient.py

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, timeout

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs
DGRAM_PORT = 56765  # The same port as used by the server


def discover(dgram_port):
    with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
        s.settimeout(10)
        s.bind(('', dgram_port))
        try:
            data, _ = s.recvfrom(1024)  # wait for a packet
            if str(data, 'utf-8').startswith(MAGIC):
                rc = str(data[len(MAGIC):], 'utf-8').split(':')
                return rc[0], rc[1], int(rc[2])
        except timeout:
            print('Connection attempt timed out')
            return None, None, None


def run():
    host, ip, port = discover(DGRAM_PORT)
    if not host:
        print('Requested service not found on LAN')
        return
    print('Connecting to {} ({}:{})'.format(host, ip, port))
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            hello = s.recv(1024)
            print('Server hello: ' + str(hello, 'utf-8'))
            s.sendall(b'Hello, world')

            data = str(s.recv(1024), 'utf-8')
            print(('Received: ' + data) if data else 'Server connection closed!')
        except Exception:
            print("{}:{} - Connection refused by server!".format(host, port))
            exit(1)


if __name__ == "__main__":
    run()
