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

class Connection:

	def __init__(self, host="localhost", port=25565, *args, **kwds):

		self.sock = socket.socket(*args, **kwds)
		self.sock.connect((host, port))

	def send(self, data):
		"""Handy function for transferring data."""
		self.sock.sendall(bytes(data+"\r\n", "utf-8"))

	def recv(self, timeout=1):
		self.sock.settimeout(timeout)

		total = []
		while True:
			data = self.sock.recv(1024)
			if not data: break
			total.append(data.decode("utf-8"))
		return "".join(total)

	def close(self):
		self.sock.close()

class Daemon:

	def __init__(self):

		daemon = self

		class RORPRequestHandler(socketserver.StreamRequestHandler):

			def handle(self):
				logging.warn("%s:%d Oncoming request." % self.client_address)
				data = self.rfile.readline().strip()
				print(data)
				self.wfile.write(bytes(eval(data).__repr__(), 'utf-8'))
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

			except:
				traceback.print_exc()

			finally:
				logging.warn("Pyrorp Daemon closed.")
				self.server.shutdown()


def connect(host="localhost", port=25565):
	return Connection(host, port)


if __name__ == "__main__":

	daemon = Daemon()
	daemon.run()