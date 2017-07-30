#!/usr/bin/env /usr/bin/python3
# discover_service.py [port]

import socket
import sys

# to make sure we don't confuse or get confused by other programs
MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"

DGRAM_PORT = 56765  # The same port as used by the server


def discover(dgram_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(10)
        s.bind(('', dgram_port))
        try:
            data, _ = s.recvfrom(1024)  # wait for a packet
            if str(data, 'utf-8').startswith(MAGIC):
                rc = str(data[len(MAGIC):], 'utf-8').split(':')
                return rc[0], rc[1], int(rc[2])
        except socket.timeout as ex:
            print('Connection attempt {}'.format(ex))
            return None, None, None


def run(dgram_port):
    host, ip, port = discover(dgram_port)
    if host:
        print('Service announcement received from {} ({}:{})'.format(host, ip, port))
    else:
        print('No service announcement received')


if __name__ == "__main__":
    try:
        dgram_port = int(sys.argv[1]) if len(sys.argv) > 1 else DGRAM_PORT
    except:
        print("Invalid port {}! Using default({})".format(sys.argv[1], DGRAM_PORT))
        dgram_port = DGRAM_PORT

    run(dgram_port)
