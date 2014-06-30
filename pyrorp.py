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
import sys

class Connection:

	def __init__(self, sock, *args, **kwds):

		self.sock = sock
		self.addr = self.sock.getpeername()

	def write(self, data):
		"""Handy function for transferring data."""
		self.sock.sendall(bytes(str(data)+"\000\000", "utf-8"))

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
				if data.endswith("\000\000") or data == "":
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
				req = self.conn.read(timeout=0.5)
				res = daemon.serve(req)
				print('writing')
				self.conn.write(res)

		self.RORPRequestHandler = RORPRequestHandler
		self.refs = {"about" : "Pyrorp Daemon"}

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

	def register(self, obj, name=None):
		"""
		Register an object by given name(id if name not given)
		"""
		name = str(id(obj)) if not name else name
		self.refs[name] = obj
		return name

	def simple_serve(self, req):
		try:
			res = repr(eval(req))
		except:
			res = traceback.format_exc()
		return res

	def serve(self, req):
		print(req)
		req = json.loads(req)
		ref_list = req["ref"].split(".")
		target = self if ref_list[0] == "" else self.refs[ref_list[0]]
		try:
			for i in ref_list[1:]:
				target = getattr(target, i)

			if "args" in req or "kwds" in req:

				target = target(*req["args"], **req["kwds"])
				res = req.copy()
				res.update({
					"ref": self.register(target),
					})
				if isinstance(target, int) or isinstance(target, str):
					res.update({
						"ps" : repr(target)
						})
				res = json.dumps(res)

			else:

				res = req.copy()

			#tar = eval(req["ref"], locals=self.refs)
		except:
			traceback.print_exc()
			res = json.dumps({
				"ref" : req["ref"], 
				"error": traceback.format_exc(), 
				})

		return res


#
class _RemoteObject:

	def __init__(self, conn, ref):
		self.__dict__["conn"] = conn
		self.__dict__["ref"] = ref

	def __getattr__(self, name):
		ref = self.ref+"."+name
		req = json.dumps({"ref": ref,})
		res = json.loads(self.conn.request(req))

		if "error" in res: 
			sys.stderr.write(res["error"])
			raise AttributeError()
			return

		elif "ps" in res: # "ps" means that object is a simple object
			return res["ps"]

		return _RemoteObject(self.conn, ref)

	def __setattr__(self, name, value):

###
		req = json.dumps({
			"ref": self.ref+"."+"__setattr__",
			"args": [name, value],
			"kwds":{},
			})

		res = json.loads(self.conn.request(req))

		if "error" in res: 
			sys.stderr.write(res["error"])
			raise AttributeError()
			return

		return	

	def __repr__(self):

		req = json.dumps({
			"ref": self.ref+"."+"__repr__",
			"args": [],
			"kwds":{},
			})

		res = json.loads(self.conn.request(req))
		print(res)
		return res["ps"]

def connect(host="localhost", port=25565, *args, **kwds):
	sock = socket.socket(*args, **kwds)
	sock.connect((host, port))
	return Connection(sock)

def refer(host="localhost", port=25565):
	conn = connect(host, port)
	return _RemoteObject(conn, "") # "" indicates the daemon itself

if __name__ == "__main__":

	daemon = Daemon()
	daemon.run()