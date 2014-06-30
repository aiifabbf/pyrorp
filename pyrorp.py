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
		self.sock.sendall(bytes(data+"\000\000", "utf-8"))

	def readlines(self, **kwds):
		"""
		timeout:
		0 means non-blocking
		None means blocking
		"""
		timeout = kwds.get("timeout", None)
		if timeout == None: 
			self.sock.setblocking(True)
		else:
			self.sock.settimeout(timeout)

		buffer = []
		while True:
			try:
				data = self.sock.recv(1024).decode("utf-8")
				if data.endswith("\000\000"):
					buffer.append(data[:-2])
					break
				buffer.append(data)
			except:
				logging.debug(traceback.format_exc())
				break
		return buffer

	def read(self, **kwds):
		return "".join(self.readlines(**kwds))

	def close(self):
		self.sock.close()
	
	def open(self):
		self.sock = socket.socket()
		self.sock.connect(self.addr)

	def request(self, data, **kwds):
		self.open()
		self.write(data)
		res = self.read(**kwds)
		self.sock.close()
		return res

class Daemon:

	def __init__(self):

		daemon = self

		class RORPRequestHandler(socketserver.BaseRequestHandler):

			def handle(self):
				logging.warn("%s:%d Oncoming request." % self.client_address)
				self.conn = Connection(self.request)
				print("reading")
				req = self.conn.read()
				res = daemon.serve(req)
				print('writing')
				self.conn.write(res)

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
				logging.debug(traceback.format_exc())

			finally:
				logging.warn("Pyrorp Daemon closed.")
				self.server.shutdown()
				break

	def serve(self, req):
		try:
			res = repr(eval(req))
		except:
			res = traceback.format_exc()
		return res


def connect(host="localhost", port=25565, *args, **kwds):
	sock = socket.socket(*args, **kwds)
	sock.connect((host, port))
	return Connection(sock)


if __name__ == "__main__":

	daemon = Daemon()
	daemon.run()