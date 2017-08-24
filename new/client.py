#!/usr/bin/env /usr/bin/python3
# client.py [port]

import socket
import sys
from time import sleep
from random import random

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"
BROADCAST_PORT = 56765

HOST = ''  # Symbolic name meaning all available interfaces on localhost
DEFAULT_PORT = 55555  # Arbitrary non-privileged port

BUF_SIZE = 1024

servers = dict()

def get_ip():
	ip = '127.0.0.1'
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		try:
			s.connect(('10.255.255.255', 1))
			ip = s.getsockname()[0]
		except:
			pass
	return ip


class DiscoverService:
	def __init__(self, sock, port):
		self.sock = sock
		self.port = port
		self.hostname = socket.gethostname()
		self.ip = get_ip()
		self.data = ''

	def run(self):
		self.data = '{}{}:{}:{}'.format(MAGIC, self.hostname, self.ip, self.port).encode('ascii')
		self.sock.sendto(self.data, ('<broadcast>', BROADCAST_PORT))

	def response(self):
		return self.port


class DiscoverService1:
	def __init__(self, port, timeout_max=5.0, timeout_min=1.0):
		self.port = port
		self.hostname = socket.gethostname()
		self.ip = get_ip()
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.bind(('', 0))
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self._sock.settimeout(timeout_min + random() * (timeout_max - timeout_min))
		self.servers = {}

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

	def __enter__(self):
		return self

	def announce(self):
		data = '{}{}:{}:{}'.format(MAGIC, self.hostname, self.ip, self.port)
		self._sock.sendto(data.encode('ascii'), ('<broadcast>', BROADCAST_PORT))

	def discover(self):
		try:
			data = self._sock.recvfrom(BUF_SIZE)
			ip, port = str(data[0], 'utf-8').split(':')
			if not ip in self.servers:
				self.servers[ip] = (ip, port)
			return (ip, port)
		except socket.timeout:
			return (None, None)

	def run(self):
		self.announce()
		self.discover()

	def response(self):
		return self.port


def run1(server_port):
	while True:
		with DiscoverService1(server_port, timeout_max=5.0) as ds:
			ds.announce()
			server, port = ds.discover()
			if server:
				print('Server: {}:{}'.format(server, port))
			else:
				sleep(10 * random())

def run(server_port):
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.bind(('', 0))
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		a = DiscoverService(s, server_port)
		while True:
			a.run()
			s.settimeout(random() * 10.0)
			try:
				data = s.recvfrom(BUF_SIZE)
				ip, port = str(data[0], 'utf-8').split(':')
				if ip in servers:
					sleep(10)
				else:
					servers[ip] = (ip, port)
					print('Server: {}:{}'.format(ip, port))
			except socket.timeout:
				sleep(10)
				continue



if __name__ == "__main__":

	server_port = DEFAULT_PORT
	ip = get_ip()

	if len(sys.argv) > 1:
		try:
			server_port = int(sys.argv[1])
		except:
			print('{}: bad port. Using default ({})'.format(sys.argv[1], server_port))

	run1(server_port)
