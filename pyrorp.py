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

"""
Base RORP Message

The dict should include the following aspect:

*Essential
"ref" represents the object to be referred to.
	if ref is "", this means it refers to the root daemon, and ".attr" is a pseudo attribute of
	the daemon(not kept in daemon.__dict__ but actually kept in daemon.refs & if you want to access
	daemon's attributes, you SHOULD register daemon itself. This is for safety consideration.)

*Optional
"args" and "kwds" represent method arguments and keyword arguments.
	When these two exist in the message, this means what the "ref" represents is a callable object 
	in the remote machine. 
	
	The reason why RORP is intended to be a 'symmetric' & 'transparent' protocol lies in that 
	args" and "kwds" can contain complex local objects as well. However, the way implementing it is
	not serialising the object and transferring them to the other side like most RPC mechanisms do but
	making another request message for remote side to send to local side (because of Python 'duck'
	philosophy, we believe object eventually performs in specific aspects, e.g. when you 'print(an_object)'
	you don't actually need all of the object, you just need a reference to that object saying 'Ahh, I 
	got you' and request the object 'Please return your __repr__() result!')

"ps" represents simple object content.
	When 'ps' exists, this means the referred-to object is string or number that can be easily transferred
	over the net. This is for performance and speed concerns.

"""
BaseRORPMsg = {
	"ref" : None, 
}

"""
Pyrorp Exceptions
"""
class PyrorpBaseException(Exception):
	pass


"""
Connection layer & data transfer mechanism
"""
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


"""
Server side - Daemon
"""
class Daemon:

	def __init__(self):

		daemon = self

		class RORPRequestHandler(socketserver.BaseRequestHandler):

			def handle(self):
				#logging.warn("%s:%d Oncoming request." % self.client_address)
				self.conn = Connection(self.request)
				#print("reading")
				req = self.conn.read(timeout=0.01)
				res = daemon.serve(req)
				#print('writing')
				self.conn.write(res)

		self.RORPRequestHandler = RORPRequestHandler
		self.refs = {
		"__repr__" : self.__repr__,
		"print" : print,
		"sys" : sys,
		}

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
		#print(req)
		req = json.loads(req)
		ref_list = req["ref"].split(".")
		res = req.copy()
		if ref_list[0] == "":
			target = self.refs[ref_list[1]]
			for i in ref_list[2:]:
				target = getattr(target, i)

			res.update({
				"ref" : ".".join(ref_list[1:]),
				})
		else:
			target = self.refs[ref_list[0]]
			for i in ref_list[1:]:
				target = getattr(target, i)
		try:

			if "args" in req or "kwds" in req:

				target = target(*req["args"], **req["kwds"])
				res.update({
					"ref": self.register(target),
					})
				if isinstance(target, int) or isinstance(target, str):
					res.update({
						"ps" : repr(target)
						})
				res = json.dumps(res)


			#tar = eval(req["ref"], locals=self.refs)
		except:
			traceback.print_exc()
			res = json.dumps({
				"ref" : req["ref"], 
				"error": traceback.format_exc(), 
				})

		return res

"""
Client side - RemoteObject
Wrapper over RORP messages & Language specific implementation
"""
#
class _RemoteObject:

	def __init__(self, conn, ref):

		self.__dict__["conn"] = conn
		self.__dict__["ref"] = ref

	def __getattr__(self, name):

		targetName = self.ref + "." + name
		req = BaseRORPMsg.copy()
		req["ref"] = targetName

		res = _rorp_parseJSON(self.conn.request(_rorp_makeJSON(req)))

		if "error" in res: 
			sys.stderr.write(res["error"])
			raise AttributeError()
			return

		elif "ps" in res: # "ps" means that object is a simple object
			return res["ps"]

		return _RemoteObject(self.conn, res["ref"])

	def __setattr__(self, name, value):
##
		req = BaseRORPMsg.copy()
		req.update({
			"ref" : self.ref + "." + "__setattr__",
			"args" : [name, value],
			"kwds" : {},
			})

		res = _rorp_parseJSON(self.conn.request(_rorp_makeJSON(req)))

		if "error" in res: 
			sys.stderr.write(res["error"])
			raise AttributeError()
			return

		return	

	def __repr__(self):

		req = BaseRORPMsg.copy()
		req.update({
			"ref": self.ref + "." + "__repr__",
			"args" : [],
			"kwds" : {},
			})

		res = _rorp_parseJSON(self.conn.request(_rorp_makeJSON(req)))
		#print(res)
		return res["ps"]

	def __call__(self, *args, **kwds):

		req = BaseRORPMsg.copy()
		req.update({
			"ref": self.ref + "." + "__call__",
			"args" : args,
			"kwds" : kwds,
			})

		res = _rorp_parseJSON(self.conn.request(_rorp_makeJSON(req)))
		#print(res)
		return _RemoteObject(self.conn, res["ref"])

"""
Functions
"""
def _rorp_parseJSON(data):
	data.replace("\'", "\"")
	return eval(data)

def _rorp_makeJSON(data):
	return json.dumps(data, ensure_ascii=False)

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