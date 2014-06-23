# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import socket
import time

sock = socket.socket()
#sock.setblocking(0)

try:
	sock.connect(("localhost",25565))
	sock.sendall(bytes("HI"*900, 'utf-8'))
	#print(sock.recv(2))

finally:
	sock.close()