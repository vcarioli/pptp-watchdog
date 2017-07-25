#!/usr/bin/env /usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostname
from sys import argv, exit
from threading import Thread
from os import system, fork, getpid
from signal import signal, SIGINT

from time import sleep

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"
BROADCAST_PORT = 56765

HOST = ''  # Symbolic name meaning all available interfaces on localhost
DEFAULT_PORT = 55555  # Arbitrary non-privileged port

BUF_SIZE = 1024


def announcer(port):
	with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
		s.bind(('', 0))
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # this is a broadcast socket
		# data = '{}{}'.format(MAGIC, port).encode('ascii')
		data = '{}{}:{}'.format(MAGIC, gethostname(), port).encode('ascii')
		s.sendto(data, ('<broadcast>', BROADCAST_PORT))


def announce_service(port, server_control):
	while server_control['continue']:
		t = Thread(target=announcer, args=(port,))
		t.start()
		t.join()
		sleep(5)


# Service function for handling connections.
def talk_service(client_sock, server_control):
	client_sock.send(b'HELLO')  # Send message to connected client
	data = str(client_sock.recv(BUF_SIZE), 'utf-8')  # Receiving from client

	cmd = 'ping -c 1 -w 2 -q pptp > /dev/null 2>&1'
	try:
		if not data or data == '.':
			server_control['continue'] = False
			data = 'Server stopping'
		else:
			data = "pptp {}pinging".format("not " if system(cmd) else "")
	except:
		pass
	finally:
		client_sock.sendall(data.encode('ascii'))
		client_sock.close()


def listener_service(s, server_control):
	s.listen(5)  # Start listening on socket

	# Keep talking with the client
	while server_control['continue']:
		try:
			# blocking call - wait to accept a connection
			client_sock, _ = s.accept()

			# Someone connected - start talk_service thread
			t = Thread(target=talk_service, args=(client_sock, server_control))
			t.start()
			t.join()
		except:
			return


def sigint_handler(sig, frame):
	exit(0)


def run(host, port):
	signal(SIGINT, sigint_handler)

	server_control = {'continue': True}

	Thread(target=announce_service, name='announcer', args=(port, server_control)).start()

	with socket(AF_INET, SOCK_STREAM) as s:
		try:
			s.bind((host, port))
		except Exception as ex:
			print('Bind failed. Error: {} - {}'.format(ex.errno, ex.strerror))
			exit(1)

		listener = Thread(target=listener_service, args=(s, server_control))
		listener.start()

		# main control loop
		while True:
			if not server_control['continue']:
				return

			# other controls

			listener.join(1)


def get_ip():
	ip = '127.0.0.1'
	with socket(AF_INET, SOCK_DGRAM) as s:
		try:
			s.connect(('10.255.255.255', 1))
			ip = s.getsockname()[0]
		except:
			pass
	return ip


if __name__ == "__main__":
	pid = fork()
	if pid > 0:  # successfull fork(): parent process exits
		exit(0)
	elif pid < 0:  # unsuccessfull fork(): print error message (should never happen)
		print('error: fork() returned {}'.format(pid))
		exit(pid)
	else:  # successfull fork(): get child's pid
		pid = getpid()

	server_port = DEFAULT_PORT
	if len(argv) > 1:
		try:
			server_port = int(argv[1])
		except:
			print('{}: bad port. Using default ({})'.format(argv[1], server_port))

	# find server IP
	ip = get_ip()

	print('{} (IP: {}) starts listening on port {} (PID: {})'.format(gethostname(), ip, server_port, pid))
	run(HOST, server_port)
	print('Server {}:{} (IP: {}) dying.'.format(gethostname(), server_port, ip))

	exit(0)
