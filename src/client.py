# client.py

import datetime
import time

from core import Socket

sock = Socket()
sock.connect('0.0.0.0', 50011)
while True:
	sock.send(str(datetime.datetime.now()))
	time.sleep(5)