import unittest
import socket
import neronet.nerokid
import os

class TestSpecifyExperiments(unittest.TestCase):
        
    def setUp(self):
        self.testKid = neronet.nerokid.NeroKid()

    def test_server_gets_data(self):
        sock = socket.socket()
        sock.settimeout(5.0)
        sock.bind(('localhost', 0))
        sock.listen(1)
        host, port = sock.getsockname()
        command = "nerokid %s %d sleep.py 1 1 &" % (host, port)
        os.system(command)
        newsock, asd = sock.accept()
        data = newsock.recv(2048)
        sock.close()
        newsock.close()
        self.assertTrue(data)

    def test_socket_initialize(self):
        with self.assertRaises(ValueError):
            self.testKid.initialize_socket()

if __name__ == '__main__':
        unittest.main()