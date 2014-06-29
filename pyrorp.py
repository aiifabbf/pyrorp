# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import socketserver # For continous stream
import socket
import traceback
import logging
import time
import json

def _rorp_decode(msg):
	pass

class Connection:

	def __init__(self, sock, *args, **kwds):

		self.sock = sock
		self.addr = self.sock.getpeername()

	def write(self, data):
		"""Handy function for transferring data."""
		self.sock.sendall(bytes(data, "utf-8"))

	def readlines(self, **kwds):
		self.sock.settimeout(kwds.get("timeout", 1))

		buffer = []
		while True:
			try:
				data = self.sock.recv(1024).decode("utf-8")
				if data == "":
					buffer.append(data[:-1])
					break
				buffer.append(data)
			except:
				traceback.print_exc()
				break
		return buffer

	def read(self, **kwds):
		return "".join(self.readlines(**kwds))

	def close(self):
		self.sock.close()
	
	def open(self):
		self.sock = socket.socket()
		self.sock.connect(self.addr)

class Daemon:

	def __init__(self):

		daemon = self

		class RORPRequestHandler(socketserver.BaseRequestHandler):

			def handle(self):
				logging.warn("%s:%d Oncoming request." % self.client_address)
				self.conn = Connection(self.request)
				data = self.conn.read(timeout=0.1)
				self.conn.write(eval(data).__repr__())
				print(data)
				print("Returned")

		self.RORPRequestHandler = RORPRequestHandler

	def run(self, **kwds):

		host = kwds.get("host", "0.0.0.0")
		port = kwds.get("port", 25565)

		self.server = socketserver.TCPServer((host, port), self.RORPRequestHandler)

		logging.warn("%s:%d Pyrorp Daemon started." % (host, port))

		while True:
			try:
				self.server.serve_forever()

			except KeyboardInterrupt:
				logging.warn("KeyboardInterrupt!")

			except:
				traceback.print_exc()

			finally:
				logging.warn("Pyrorp Daemon closed.")
				self.server.shutdown()
				break


def connect(host="localhost", port=25565, *args, **kwds):
	sock = socket.socket(*args, **kwds)
	sock.connect((host, port))
	return Connection(sock)


if __name__ == "__main__":

	daemon = Daemon()
	daemon.run()