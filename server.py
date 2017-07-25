#!/usr/bin/env /usr/bin/python3

import sys
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostname
from sys import exit
from threading import Thread
from os import system, fork, getpid
from signal import signal, SIGINT

from time import sleep

HOST = ''  # Symbolic name meaning all available interfaces on localhost
DEFAULT_PORT = 5000  # Arbitrary non-privileged port
BUF_SIZE = 1024

MAGIC = "fna349fn" # to make sure we don't confuse or get confused by other programs

def announcer(port):
    with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
        data = '{}pptp watchdog service available on port {}'.format(MAGIC, port).encode('ascii')
        s.sendto(data, ('<broadcast>', port))

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

	cmd = 'ping -c 1 -q pptp > /dev/null 2>&1'
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
	sys.exit(0)


def run(host, port):
	server_control = {'continue': True}

	signal(SIGINT, sigint_handler)

	announcer = Thread(target=announce_service, args=(port, server_control))
	announcer.start()
    
	with socket(AF_INET, SOCK_STREAM) as s:
		try:
			s.bind((host, port))
		except Exception as ex:
			print('Bind failed. Error: {} - {}'.format(ex.errno, ex.strerror))
			sys.exit(1)

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
		sys.exit(0)
	elif pid < 0:  # unsuccessfull fork(): print error message (should never happen)
		print('error: fork() returned {}'.format(pid))
		sys.exit(pid)
	else:  # successfull fork(): get child's pid
		pid = getpid()

	try:
		server_port = int(sys.argv[1])
	except:
		server_port = DEFAULT_PORT

	# find server IP
	ip = get_ip()

	print('{} (IP: {}) starts listening on port {} (PID: {})'.format(gethostname(), ip, server_port, pid))
	run(HOST, server_port)
	print('Server {}:{} (IP: {}) dying.'.format(gethostname(), server_port, ip))

	sys.exit(0)
