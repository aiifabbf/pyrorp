# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import socketserver # For continous stream
import traceback
import logging

class RORPRequestHandler(socketserver.StreamRequestHandler):

	def handle(self):

		data = self.rfile.read().strip()
		print(data)
		self.wfile.write(bytes("OK", 'utf-8'))
		print("Returned")

class Daemon:

	def __init__(self):

		pass

	def run(self, **kwds):

		host = kwds.get("host", "")
		port = kwds.get("port", 25565)

		self.server = socketserver.TCPServer((host, port), RORPRequestHandler)

		logging.warn("Pyrorp Daemon started@%s:%d" % ("localhost" if not host else host, port))

		while True:
			try:
				self.server.serve_forever()

			except:
				traceback.print_exc()

			finally:
				logging.warn("Pyrorp Daemon closed.")
				self.server.shutdown()


if __name__ == "__main__":

	daemon = Daemon()
	daemon.run()