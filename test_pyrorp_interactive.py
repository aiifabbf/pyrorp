# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import pyrorp
import time

daemon = pyrorp.refer()

while True:
	data = input("Pyrorp>> ")
	print(daemon.eval(data))
