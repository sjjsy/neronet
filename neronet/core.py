# core.py
#
# Core class and function definitions

import os
import sys
import datetime
import socket
import pickle
import time
#import psutil
from signal import signal, SIGTERM, SIGQUIT
from traceback import print_exc
from pathlib import Path

TIMEOUT = 5.0
"""float: how long the socket waits before failing when sending data
"""


def osrun(cmd):
    print('> %s' % (cmd))
    os.system(cmd)


class Logger:

    """A class to simplify logging."""

    def __init__(self, name):
        self.name = name

    def log(self, msg):
        """prints datetime, process name, process message"""
        # Print to stdout in a clear format
        print('%s %s: %s' % (datetime.datetime.now(), self.name, msg))


class Socket:

    """A class to simplify socket usage."""

    def __init__(self, host, port):
        # Save key attributes
        self.host = host
        self.port = port

    def send_data(self, data):
        """Create a socket, send data over it, and close it"""
        # Create a TCP/IP socket
        sock = socket.socket()
        sock.settimeout(TIMEOUT)
        # Connect to the mother
        #self.logger.log('Connecting to (%s, %s)...' % (self.host, self.port))
        sock.connect((self.host, self.port))
        # Send data
        #self.logger.log('Sending data "%s"...' % (data))
        sock.sendall(pickle.dumps(data, -1))
        # Close socket
        #self.logger.log('Closing socket...')
        sock.close()

class Experiment():
    def __init__(self, experiment_id, path, runcmd):
        self.experiment_id = experiment_id
        self.path = path
        self.runcmd = runcmd
        self.state = None