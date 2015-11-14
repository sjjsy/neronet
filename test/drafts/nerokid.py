# nerokid.py
#
# one line description
HOST = '0.0.0.0' # Symbolic name meaning all available interfaces
PORT = 50007 # Arbitrary non-privileged port

import socket
import os
import subprocess


class NeroKid(object):

  def __init__(self):
    """"""
    self.s = None
    self.conn = None
    self.addr = None
    pass

  def run(self):
    """The Nerokid main."""
    ##self.initialize_socket()
    self.launch_child_process()
    #self.send_data_to_neromum()

  def initialize_socket(self):
    """initialize socket"""
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind(('0.0.0.0', 50008)) # binds socket to port
    print("waiting for connetion")
    self.s.listen(1) # Listens port or incoming tcp connections
    self.conn, self.addr = self.s.accept() # Accepts connection and saves handle and address of recipent

  def send_data_to_neromum(self ):
    """Send status data to Neromum."""
    self.conn.sendall(self.proc.communicate()[0])

  def launch_child_process(self ):
    """Launches received script"""
    file = open("tsti_results.txt", "w")
    #self.proc = subprocess.Popen(['python3','tsti.py'],universal_newlines=True, stdout=file)
    self.proc = subprocess.Popen(['python3','tsti.py'])

  def collect_std_out_data(self):
    """Collect data what child process outputs"""
    pass
  
if __name__ == '__main__':
  NeroKid().run()