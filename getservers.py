#!/usr/bin/env /usr/bin/python3
# discover_service.py [port]

import socket
import sys

from random import random
from time import sleep
from threading import Thread, Event

# to make sure we don't confuse or get confused by other programs
MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"

BROADCAST_PORT = 56765  # The same port as used by the server


def get_ip():
	ip = '127.0.0.1'
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		try:
			s.connect(('10.255.255.255', 1))
			ip = s.getsockname()[0]
		except:
			pass
	return ip


def discover(dgram_port):
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.bind(('', 0))
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		data = '{}{}:{}'.format(MAGIC, socket.gethostname(), get_ip()).encode('ascii')
		s.sendto(data, ('<broadcast>', BROADCAST_PORT))

		try:
			data, _ = s.recv(1024)  # wait for a packet
			if str(data, 'utf-8').startswith(MAGIC):
				rc = str(data[len(MAGIC):], 'utf-8').split(':')
				return rc[0], rc[1], int(rc[2])
		except socket.timeout as ex:
			print('Connection attempt {}'.format(ex))
			return None, None, None

def run():
	host, ip, port = discover(BROADCAST_PORT)
	if host:
		print('Service announcement received from {} ({}:{})'.format(host, ip, port))
	else:
		print('No service announcement received')


if __name__ == "__main__":
	try:
		dgram_port = int(sys.argv[1]) if len(sys.argv) > 1 else BROADCAST_PORT
	except:
		print("Invalid port {}! Using default({})".format(sys.argv[1], BROADCAST_PORT))
		dgram_port = BROADCAST_PORT

	run()
