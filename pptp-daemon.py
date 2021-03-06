#!/usr/bin/env /usr/bin/python3
# pptp-daemon.py [port]

import atexit
import fcntl
import os
import resource
import signal
import socket
import sys

from time import sleep
from threading import Thread, Event
from random import random

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"
BROADCAST_PORT = 56765

HOST = ''  # Symbolic name meaning all available interfaces on localhost
DEFAULT_PORT = 55555  # Arbitrary non-privileged port

BUF_SIZE = 1024


def daemonize(pidfile=None):
	try:
		pid = os.fork()  # fork first child
	except OSError as e:
		raise Exception("%s [%d]".format(e.strerror, e.errno))

	if pid == 0:  # first child
		os.setsid()
		signal.signal(signal.SIGHUP, signal.SIG_IGN)

		try:
			pid = os.fork()  # fork second child
		except OSError as e:
			raise Exception("%s [%d]".format(e.strerror, e.errno))
		if pid == 0:
			pf = None
			if pidfile:
				try:
					pf = open(pidfile, 'w')
					pf.write('{}\n'.format(os.getpid()))
					pf.flush()
					fcntl.lockf(pf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
					atexit.register(lambda x: fcntl.lockf(x.fileno(), fcntl.LOCK_UN), pf)
					atexit.register(lambda x: os.close(x.fileno()), pf)
					atexit.register(lambda x: os.remove(x), pidfile)
				except OSError:
					print('\n{} is locked!\nAnother instance is already running, exiting!'.format(pidfile), )
					sys.exit(1)

			os.chdir("/")
			os.umask(0)

			# Iterate through and close all file descriptors.
			for fd in range(0, resource.getrlimit(resource.RLIMIT_NOFILE)[1]):
				try:
					if not pf or fd != pf.fileno():
						os.close(fd)
				except OSError:  # Ignore ERROR: fd wasn't open
					pass

			os.open(os.devnull, os.O_RDWR)  # Redirect stdin to /dev/null
			os.dup2(0, 1)  # Duplicate stdin to stdout (1)
			os.dup2(0, 2)  # Duplicate stdin to stderr (2)

			# return to main program
			return 0
		else:  # exit second parent
			os._exit(0)
	else:  # exit first parent
		os.wait()
		os._exit(0)

	return 0


def get_ip():
	ip = '127.0.0.1'
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		try:
			s.connect(('10.255.255.255', 1))
			ip = s.getsockname()[0]
		except:
			pass
	return ip


class ServiceExit(Exception):
	"""
	Custom exception which is used to trigger the clean exit
	of all running threads and the main program.
	"""
	pass


class ServiceBase(Thread):
	def __init__(self, port, shutdown_flag, name):
		Thread.__init__(self, name=name)
		self.port = port
		self.shutdown_flag = shutdown_flag

	def terminate(self):
		return self.shutdown_flag.is_set()


class AnnounceService(ServiceBase):
	def __init__(self, port, shutdown_flag):
		ServiceBase.__init__(self, port, shutdown_flag, 'announce_service')

	def run(self):
		while not self.terminate():
			with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
				s.bind(('', 0))
				s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
				data = '{}{}:{}:{}'.format(MAGIC, socket.gethostname(), get_ip(), self.port).encode('ascii')
				s.sendto(data, ('<broadcast>', BROADCAST_PORT))
				sleep(random() * 2.5)


class ListenerService(ServiceBase):
	def __init__(self, host, port, shutdown_flag):
		ServiceBase.__init__(self, port, shutdown_flag, 'listener_service')
		self.host = host
		# self.ping = 'ping -c 1 -w 2 -q pptp > /dev/null 2>&1'
		self.ping = 'true'

	# Service function for handling connections.
	def talk_service(self):
		self.client_sock.send(b'HELLO')  # Send message to connected client
		data = str(self.client_sock.recv(BUF_SIZE), 'utf-8')  # Receiving from client

		try:
			if not data or data == '.':
				self.shutdown_flag.set()
				data = 'Server stopping'
			else:
				data = 'pptp{}pinging'.format(' not ' if os.system(self.ping) else ' ')
		except:
			pass
		finally:
			self.client_sock.sendall(data.encode('ascii'))
			self.client_sock.close()

	def run(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			try:
				s.bind((self.host, self.port))
			except Exception as ex:
				print('Bind failed. Error: {}'.format(ex))
				self.shutdown_flag.set()  # raise ServiceExit
				return

			s.listen(5)

			# Keep talking with the client
			while not self.terminate():
				# blocking call - wait to accept a connection
				self.client_sock, _ = s.accept()

				# Someone connected - start talk_service thread
				t = Thread(target=self.talk_service, name='talk_service')
				t.start()
				t.join()


def sigint_handler(sig, frame):
	raise ServiceExit


def run(port):
	shutdown_flag = Event()

	terminate = lambda: shutdown_flag.is_set()

	listener_thread = ListenerService(HOST, port, shutdown_flag)
	announcer_thread = AnnounceService(port, shutdown_flag)
	try:
		listener_thread.start()
		if not listener_thread.is_alive():
			return
		announcer_thread.start()

		# main control loop
		while not terminate():
			sleep(random() * 2.0)	# keep main thread alive
	finally:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			try:
				s.connect((get_ip(), port))
			except Exception:
				print('Server {}:{} stopped!'.format(get_ip(), port))
				sys.exit(0)

		announcer_thread.join(5)
		listener_thread.join(5)


if __name__ == "__main__":

	PIDFILE = '/var/run/user/{}/pptp-server.pid'.format(os.getuid())
	server_port = DEFAULT_PORT
	ip = get_ip()

	if len(sys.argv) > 1:
		try:
			server_port = int(sys.argv[1])
		except:
			print('{}: bad port. Using default ({})'.format(sys.argv[1], server_port))

	signal.signal(signal.SIGINT, sigint_handler)

	daemonize(PIDFILE)

	#	print('{} (IP: {}) starts listening on port {}'.format(gethostname(), ip, server_port))
	#	import syslog
	#	syslog.syslog('{} (IP: {}) starts listening on port {}'.format(gethostname(), ip, server_port))

	run(server_port)
