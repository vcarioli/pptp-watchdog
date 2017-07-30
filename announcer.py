#!/usr/bin/env /usr/bin/python3

import atexit
import fcntl
import os
import resource
import signal
import socket
import sys

from random import random
from time import sleep
from threading import Thread, Event

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"
BROADCAST_PORT = 56765

HOST = ''  # Symbolic name meaning all available interfaces on localhost
DEFAULT_PORT = 55555  # Arbitrary non-privileged port

shutdown_flag = Event()


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


def signal_handler(sig, frame):
	shutdown_flag.set()


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
				s.bind(('', BROADCAST_PORT))
				data, _ = s.recvfrom(1024)  # wait for a packet
				if str(data, 'utf-8').startswith(MAGIC):
					rc = str(data[len(MAGIC):], 'utf-8').split(':')
					data = '{}{}:{}:{}'.format(MAGIC, socket.gethostname(), get_ip(), self.port).encode('ascii')
					s.sendto(data, (rc[2], BROADCAST_PORT))

			sleep(random() * 0.5 + 0.5)

def _run():
	while not shutdown_flag.is_set():
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.bind(('', BROADCAST_PORT))
			data, _ = s.recvfrom(1024)  # wait for a packet
			if str(data, 'utf-8').startswith(MAGIC):
				rc = str(data[len(MAGIC):], 'utf-8').split(':')
				data = '{}{}:{}:{}'.format(MAGIC, socket.gethostname(), get_ip(), DEFAULT_PORT).encode('ascii')
				s.sendto(data, (rc[2], BROADCAST_PORT))

		sleep(random() * 0.5 + 0.5)


def run():
	terminate = lambda: shutdown_flag.is_set()

	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGINT, signal_handler)

	announcer_thread = AnnounceService(DEFAULT_PORT, shutdown_flag)
	try:
		announcer_thread.start()

		# main control loop
		while not terminate():
#			_run()
			sleep(random() * 5.0)  # keep main thread alive
	finally:
		sys.exit(0)

		announcer_thread.join(5)

if __name__ == "__main__":
	PIDFILE = '/var/run/user/{}/announcer.pid'.format(os.getuid())

	daemonize(PIDFILE)

	run()