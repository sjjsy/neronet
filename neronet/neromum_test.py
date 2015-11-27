import unittest
import neronet.neromum
import socket
import os
import pickle


class Neromum_test(unittest.TestCase):

    def setUp(self):
        self.mum = Neromum()
        self.mum.experiment = 'sleep.py'
        self.d = { "lion": "yellow", "kitty": "red" }
        self.data = pickle.dumps(self.d)
        self.mum.initialize_socket()

    def test_socket_init(self):

        self.assertTrue(self.mum.sock)
        self.assertTrue(isinstance( self.mum.port, int ))
        self.assertEqual(self.mum.host,'localhost')
        self.assertEqual(self.mum.open_incoming_connections, [mum.sock])
        self.assertEqual(self.mum.open_outgoing_connections, [])

    def test_data_from_nerokid(self):

        self.mum.start_nerokid():

    def test_parse_data(self):

        self.mum.data = self.data
        self.mum.parse_nerokid_data()
        self.assertEqual(self.mum.data, self.d)

if __name__ == '__main__':
	unittest.main()
