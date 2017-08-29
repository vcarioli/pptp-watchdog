#!/usr/bin/env /usr/bin/python3
# daemon.py

"""
	class Daemon - daemonize current process

	Usage:
		with daemon.Daemon():
			run_my_program()
"""

import atexit
import fcntl
import os
import signal
import sys


LOCK_DIR = '/var/run/user/{}'.format(os.getuid())


class Daemon:
	def __init__(self, lockfile=None, lockdir=None):
		self._lockdir = lockdir if lockdir else LOCK_DIR
		self._lockfile = os.path.join(self._lockdir, '{}.pid'.format(os.path.basename(lockfile))) if lockfile else None
		self._lock_fd = None

	def _unlock(self):
		fcntl.lockf(self._lock_fd.fileno(), fcntl.LOCK_UN)
		os.close(self._lock_fd.fileno())
		os.remove(self._lockfile)
		atexit.unregister(self._unlock)

	def _lock(self):
		if self._lockfile:
			try:
				self._lock_fd = open(self._lockfile, 'w')
				self._lock_fd.write('{}\n'.format(os.getpid()))
				self._lock_fd.flush()
				fcntl.lockf(self._lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
				atexit.register(self._unlock)
			except OSError:
				sys.exit(1)

	def _close_all_files(self):
		if getattr(sys, 'frozen', False):
			# executing as a bundle (pyinstaller)
			sys.stdout.close()
			sys.stdout = open(os.devnull, "w")
			sys.stderr.close()
			os.dup2(sys.stdout.fileno(), 2)  # Duplicate stdout to stderr (2)
		else:
			# # Iterate through and close all file descriptors.
			# from resource import getrlimit, RLIMIT_NOFILE
			# for fd in range(0, getrlimit(RLIMIT_NOFILE)[1]):
			for fd in range(0, 1024):
				try:
					if self._lock_fd and fd != self._lock_fd.fileno():
						os.close(fd)
				except OSError:  # Ignore ERROR: fd wasn't open
					continue
			os.open(os.devnull, os.O_RDWR)  # Redirect stdin to /dev/null
			os.dup2(0, 1)  # Duplicate stdin to stdout (1)
			os.dup2(0, 2)  # Duplicate stdin to stderr (2)

	def __enter__(self):
		self.daemonize()

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

	def daemonize(self):
		try:
			pid = os.fork()  # fork first child
		except OSError as e:
			raise Exception("%s [%d]".format(e.strerror, e.errno))

		if pid != 0:  # first fork
			os.waitpid(pid, 0)  # wait for child completes fork()
			os._exit(0)  # exit first parent

		os.setsid()  # run in new session
		signal.signal(signal.SIGHUP, signal.SIG_IGN)  # ignore SIGHUP

		try:
			pid = os.fork()  # fork second child
		except OSError as e:
			raise Exception("%s [%d]".format(e.strerror, e.errno))
		if pid != 0:
			os._exit(0)  # exit second parent

		os.chdir("/")
		os.umask(0)

		self._lock()
		self._close_all_files()

		return 0


if __name__ == "__main__":
	from time import sleep

	print("start")

	with Daemon('daemon'):
		print("\nsono un demone\n")	# SE TUTTO FUNZIONA NON DOVREBBE ESSERE VISUALIZZATO
		sleep(30)

#	d = Daemon(lockfile='daemon', lockdir='/home/valerio')
#	d.daemonize()
#	sleep(5)