#! / usr / bin / env / usr / bin / python3
#discover_service.py [port]

import socket
import sys
import time

from threading import Thread

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs
DGRAM_PORT = 56765  # The same port as used by the server


def discover(dgram_port):
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # create UDP socket as s:
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


class DiscoverService(Thread):
	def __init__(self, dgram_port, servers, time_out=10):
		Thread.__init__(self, name='discover_service')
		self.dgram_port = dgram_port
		self.timeout = time_out
		self.servers = servers

	def discover(self):
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # create UDP socket as s:
			s.settimeout(self.timeout)
			s.bind(('', self.dgram_port))
			rc = None
			try:
				data, _ = s.recvfrom(1024)  # wait for a packet
				if str(data, 'utf-8').startswith(MAGIC):
					rc = str(data[len(MAGIC):], 'utf-8').split(':')
					return rc[0], rc[1], int(rc[2])
			except socket.timeout as ex:
				return None, None, None

	def run(self):
		host, ip, port = self.discover()
		if host and ip not in self.servers.keys():
			self.servers[ip] = [host, ip, port]


def run(dgram_port, servers):
	from random import random
	c = 0
	keys = servers.keys
	while True:
		discover_thread = DiscoverService(dgram_port, servers=servers)
		discover_thread.start()
		if c != len(keys()):
			c = len(keys())
			print()
			for k in keys():
				print('host: {}, IP: {}, port: {}'.format(*servers[k]))
		else:
			print('.', end='', flush=True)
		discover_thread.join()
		time.sleep(random() * 1.5)


if __name__ == "__main__":
	try:
		dgram_port = int(sys.argv[1]) if len(sys.argv) > 1 else DGRAM_PORT
	except:
		print("Invalid port {}! Using default({})".format(sys.argv[1], DGRAM_PORT))
		dgram_port = DGRAM_PORT
	servers = dict()
	run(dgram_port, servers)
