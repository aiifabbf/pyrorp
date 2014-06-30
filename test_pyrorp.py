# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import pyrorp
import time

conn = pyrorp.connect()
conn.write("1+1")
print(conn.read())
conn.close()

conn.open()
conn.write("1+1")
print(conn.read())

print(conn.request("1+1"))