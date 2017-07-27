#!/usr/bin/env /usr/bin/python3
# discover_service.py [port]

from socket import socket, AF_INET, SOCK_DGRAM, timeout as timeout_expired
from sys import argv
from threading import Thread
from time import sleep

MAGIC = "426e4973-a87c-46ca-b369-442e4cc50254"  # to make sure we don't confuse or get confused by other programs

DGRAM_PORT = 56765  # The same port as used by the server


def discover(dgram_port):
    with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
        s.settimeout(10)
        s.bind(('', dgram_port))
        try:
            data, _ = s.recvfrom(1024)  # wait for a packet
            if str(data, 'utf-8').startswith(MAGIC):
                rc = str(data[len(MAGIC):], 'utf-8').split(':')
                return rc[0], rc[1], int(rc[2])
        except timeout_expired as ex:
            print('Connection attempt {}'.format(ex))
            return None, None, None


class DiscoverService(Thread):
    def __init__(self, dgram_port, time_out=10):
        Thread.__init__(self, name='discover_service')
        self.dgram_port = dgram_port
        self.timeout = time_out
        self.servers = dict()

    def discover(self):
        with socket(AF_INET, SOCK_DGRAM) as s:  # create UDP socket as s:
            s.settimeout(self.timeout)
            s.bind(('', self.dgram_port))
            rc = None
            try:
                data, _ = s.recvfrom(1024)  # wait for a packet
                if str(data, 'utf-8').startswith(MAGIC):
                    rc = str(data[len(MAGIC):], 'utf-8').split(':')
                    return rc[0], rc[1], int(rc[2])
            except timeout_expired as ex:
                return None, None, None

    def run(self):
        host, ip, port = self.discover()

        if host and ip not in self.servers.keys():
            self.servers[ip] = [host, ip, port]


def run(dgram_port):
    while True:
        discover_thread = DiscoverService(dgram_port)
        c = len(discover_thread.servers.keys())
        discover_thread.start()
        discover_thread.join()
        if c != len(discover_thread.servers.keys()):
            c = len(discover_thread.servers.keys())
            for k in discover_thread.servers.keys():
                print('host: {}, IP: {}, port: {}'.format(*discover_thread.servers[k]))
        sleep(3)


if __name__ == "__main__":
    try:
        dgram_port = int(argv[1]) if len(argv) > 1 else DGRAM_PORT
    except:
        print("Invalid port {}! Using default({})".format(argv[1], DGRAM_PORT))
        dgram_port = DGRAM_PORT

    run(dgram_port)
