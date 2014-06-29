# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import pyrorp
import time

conn = pyrorp.connect()

while True:
	data = input("Pyrorp>>")
	conn.write(data)
	print(conn.read())