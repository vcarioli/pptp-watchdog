#!/usr/bin/env /usr/bin/python3
# discover_service.py [port]

from socket import socket, gethostname, AF_INET, SOCK_DGRAM
from sys import argv

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs

BROADCAST_PORT = 56765	# The same port as used by the server


def discover(port):
	with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
		s.bind(('', BROADCAST_PORT))
		data, addr = s.recvfrom(1024)  # wait for a packet
		if str(data, 'utf-8').startswith(MAGIC):
			# return (addr[0], int(data[len(MAGIC):]))
			return str(data[len(MAGIC):], 'utf-8').split(':')


def run(port):
	print('Service announcement received from {}:{}'.format(*discover(port)))


if __name__ == "__main__":
	try:
		broadcast_port = int(argv[1]) if len(argv) > 1 else BROADCAST_PORT
	except:
		print("Invalid port {}! Using default({})".format(argv[1], BROADCAST_PORT))
		broadcast_port = BROADCAST_PORT

	run(broadcast_port)
