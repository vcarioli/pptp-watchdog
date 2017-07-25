#!/usr/bin/env /usr/bin/python3
# discover_service.py [port]

from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv

DEFAULT_PORT = 55555  # The same port as used by the server
MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs


def discover(port):
	with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
		s.bind(('', port))

		data, addr = s.recvfrom(1024)  # wait for a packet
		if str(data, 'utf-8').startswith(MAGIC):
			return (addr[0], port)


def run(port):
	print('Service announcement received from {}:{}'.format(*discover(port)))


if __name__ == "__main__":
	try:
		server_port = int(argv[1]) if len(argv) > 1 else DEFAULT_PORT
	except:
		print("Invalid port {}! Using default({})".format(argv[1], DEFAULT_PORT))
		server_port = DEFAULT_PORT

	run(server_port)
