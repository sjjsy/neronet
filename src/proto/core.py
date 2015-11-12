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
        print('%s %s: %s' % (datetime.datetime.now(), self.name, msg))

class Socket:
    """A class to simplify socket usage."""
    def __init__(self, logger, host, port):
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

class SocketOLD:
    """A class to simplify socket usage."""

    def __init__(self, sock=None):
        self.sock = sock if sock else \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.sock.bind((host, port))

    def send(self, msg):
        msg_len = len(msg)
        total_sent = 0
        while total_sent < msg_len:
            sent_now = self.sock.send(msg[total_sent:])
            if sent_now == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent_now

    def receive(self, msg_len=4096):
        chunks = []
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = self.sock.recv(min(msg_len - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)