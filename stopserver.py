#!/usr/bin/env /usr/bin/python3
# dstopserver.py

from socket import socket, AF_INET, SOCK_DGRAM

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs
DGRAM_PORT = 56765  # The same port as used by the server


def discover():
    with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
        s.bind(('', DGRAM_PORT))
        data, addr = s.recvfrom(1024)  # wait for a packet
        if str(data, 'utf-8').startswith(MAGIC):
            rc = str(data[len(MAGIC):], 'utf-8').split(':')
            return rc[0], int(rc[1])



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
