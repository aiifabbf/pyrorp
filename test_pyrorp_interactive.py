# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import pyrorp
import time

while True:
	data = input("Pyrorp>> ")
	conn = pyrorp.connect()
	conn.write(data)
	print("*Sent*")
	print(conn.read())
	conn.close()