# master.py

from core import Socket

sock = Socket()
sock.connect('0.0.0.0', 50011)
while True:
	data = sock.receive()
	print('data: %s' % (data))