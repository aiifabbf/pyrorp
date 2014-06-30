# coding=utf-8
"""
Pyrorp.py

Python implementation of the Remote Object Reference Protocol

"""

import pyrorp
import time

daemon = pyrorp.refer()
print(daemon)