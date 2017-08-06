#!/usr/bin/env /usr/bin/python3
# server.py [port]

import socket
import sys
import time
import threading

from random import random

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs
DGRAM_PORT = 56765  # The same port as used by the server

DEFAULT_PORT = 55555  # Arbitrary non-privileged port


def get_ip():
	ip = '127.0.0.1'
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		try:
			s.connect(('10.255.255.255', 1))
			ip = s.getsockname()[0]
		except:
			pass
	return ip

class AnnounceService:
	def __init__(self, dgram_port):
		self.dgram_port = dgram_port
		self.clients = dict()
		self.new_clients = False
		self.client_data = ''
		self.client_addr = ()

	def _add_client(self):
		host, ip, port = self.client_data.split(':')
		if ip not in self.clients.keys():
			self.clients[ip] = [host, ip, port]
			self.new_clients = True

	def discover(self):
		self.new_clients = False
		self.client_data = ''
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.bind(('', self.dgram_port))
			data, self.client_addr = s.recvfrom(1024)  # wait for a packet
			if str(data, 'utf-8').startswith(MAGIC):
				self.client_data = str(data[len(MAGIC):], 'utf-8')
				return True
			else:
				return False

	def	send_response(self):
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.bind(('', self.dgram_port))
			data = '{}:{}'.format(get_ip(), DEFAULT_PORT).encode('ascii')
			s.sendto(data, self.client_addr)

	def run(self):
		if self.discover():
			self._add_client()
		if self.new_clients:
			self.send_response()


def run(dgram_port):
	a = AnnounceService(dgram_port)
	while True:
		a.run()
		if a.new_clients:
			print()
			for c in a.clients:
				print('host: {}, IP: {}, port: {}'.format(*a.clients[c]))
		else:
			print('.', end='', flush=True)
		time.sleep(random() * 1.5)


if __name__ == "__main__":
	try:
		dgram_port = int(sys.argv[1]) if len(sys.argv) > 1 else DGRAM_PORT
	except:
		print("Invalid port {}! Using default({})".format(sys.argv[1], DGRAM_PORT))
		dgram_port = DGRAM_PORT
	run(dgram_port)
