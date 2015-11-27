import unittest
import nerokid
import socket
import os

class TestSpecifyExperiments(unittest.TestCase):
	def Server_gets_data(self):
		sock = socket.socket()
		sock.settimeout(5.0)
		sock.bind(('localhost', 0))
		sock.listen(1)
		host, port = self.sock.getsockname()
		os.system("python3.5 %s %s sleep.py 1 1") %(host, port)
		data = sock.recv(2048)
		self.assertTrue(data)
