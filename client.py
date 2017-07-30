#!/usr/bin/env /usr/bin/python3
# client.py [host][:port]

import socket
import sys

DEFAULT_SERVER = 'localhost'
DEFAULT_PORT = 55555  # The same port as used by the server


def run(host, port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
		else:
			s.close()


if __name__ == "__main__":
	try:
		args = sys.argv[1].split(':')
		server = str(args[0]) if len(args) > 0 and args[0] != '' else DEFAULT_SERVER
		try:
			server_port = int(args[1]) if len(args) > 1 else DEFAULT_PORT
		except:
			print("Invalid port {}! Using default({})".format(args[1], DEFAULT_PORT))
			server_port = DEFAULT_PORT
	except:
		print("Using defaults for server and port ({})".format(DEFAULT_SERVER, DEFAULT_PORT))
		server = DEFAULT_SERVER
		server_port = DEFAULT_PORT

	print('Connecting to {}:{}'.format(server, server_port))
	run(server, server_port)
