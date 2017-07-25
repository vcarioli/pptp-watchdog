#!/usr/bin/env /usr/bin/python3
# stopserver.py [host][:port]

import socket
import sys

DEFAULT_SERVER = 'localhost'
DEFAULT_PORT = 55555  # The same port as used by the server


def run(host, port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		try:
			s.connect((host, port))
			s.recv(1024)  # discard 'HELLO'
			s.sendall(b'.')
			data = str(s.recv(1024), 'utf-8')
			print(data if data else 'Server connection closed!')
		except:
			print("{}:{} - Connection refused by server!".format(host, port))


if __name__ == "__main__":
	try:
		args = sys.argv[1].split(':')
		server = str(args[0]) if len(args) > 0 and args[0] != '' else DEFAULT_SERVER
		try:
			server_port = int(args[1])
		except:
			server_port = DEFAULT_PORT
	except:
		server = DEFAULT_SERVER
		server_port = DEFAULT_PORT

	print('Connecting to {}:{}'.format(server, server_port))
	run(server, server_port)
