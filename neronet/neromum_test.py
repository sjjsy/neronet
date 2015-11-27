import unittest
import neromum
import socket
import os

class Create_neromum(unittest.TestCase):
    mum = Neromum()
    mum.experiment = 'sleep.py'
    mum.initialize_socket()
    self.assertTrue(mum.sock)
    self.assertTrue(isinstance( mum.port, int ))
    self.assertTrue(mum.host == 'localhost')
    self.assertTrue(mum.open_incoming_connections == [mum.sock])
    self.assertTrue(mum.open_outgoing_connections == [])
