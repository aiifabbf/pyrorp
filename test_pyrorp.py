# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import pyrorp

conn = pyrorp.connect()
conn.send("10**900")
print(conn.recv())