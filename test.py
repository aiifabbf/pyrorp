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
	sock.sendall(bytes("1+1000\r\n", 'utf-8'))
	print(sock.recv(1024))

finally:
	sock.close()