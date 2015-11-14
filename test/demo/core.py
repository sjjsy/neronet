# core.py
#
# Core class and function definitions

import datetime
import socket
import pickle

class Logger:
    """A class to simplify logging."""
    def __init__(self, name):
        self.name = name

    def log(self, msg):
        # Print to stdout in a clear format
        print('%s %s: %s' % (datetime.datetime.now(), self.name, msg))

class Socket:
    """A class to simplify socket usage."""
    def __init__(self, logger, host, port):
        # Save key attributes
        self.logger = logger
        self.host = host
        self.port = port

    def send_data(self, data):
        # Create a TCP/IP socket
        sock = socket.socket()
        sock.settimeout(5.0)
        # Connect to the mother
        #self.logger.log('Connecting to (%s, %s)...' % (self.host, self.port))
        sock.connect((self.host, self.port))
        # Send data
        #self.logger.log('Sending data "%s"...' % (data))
        sock.sendall(pickle.dumps(data, -1))
        # Close socket
        #self.logger.log('Closing socket...')
        sock.close()
