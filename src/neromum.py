# neromum.py
#
# 

import socket
import nerokid.py
import time
from subprocess import call

class NeroMum(object):

  def __init__(self):
    """Initialize the NeroMum"""
    self.host = '10.100.43.119'
    self.port = 50007
    #self.connection, self.address

  def run(self):
    self.start_nerokid()
    self.connection, self.address = self.initialize_socket()
    while self.ask_nerokid_status() == False:
      time.sleep(5)
    else:
      data = self.retrieve_nerokid_data()
      #self.save_to_file(data, file)
    
    """The Neromum main.
    Listens for communication from Neroman or Nerokids
    and does as needed. Manages a queue of jobs by the user
    and inputs them to the Warden when there are enough 
    resources."""
    pass

  def initialize_socket(self):
    HOST = '10.100.43.119' # The remote host (my local ip)
    PORT = 50007 # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # internet, tcp
    s.connect(HOST,PORT)
    s.bind(HOST,PORT)
    s.listen(1)
    conn, addr = s.accept()
    return conn, addr
    """Initialize socket"""
    #pass

  def save_to_file(self, data, file):
    
    """Save data to the .hdf file"""
    pass

  def start_nerokid(self):
    """Start a nerokid process on a node"""
    call(["python", "nerokid.py"])
    return True 
  
  def send_data_to_neroman(self):
    """Send data to neroman on request"""
    pass
  
  def start_file_transfer(self):
    """statrs scp transfer to man"""
    pass

  def kill_child(self):
    """Because we are evil parents"""
    pass
  
  def ask_slurm_for_free_node(self):
    """See if there is a free node"""
    pass
  
  def ask_nerokid_status(self):
    """see if nerokid is done with the task"""
    conn.sendall("status")
    return conn.recv() #True or False
  
  def retrieve_nerokid_data(self):
    conn.sendall("retr_data")
    return conn.recv()
    """if any data, collect it from kid"""
    #pass

def socket_test():
  HOST = '10.100.43.119' # The remote host (my local ip)
  PORT = 50007 # The same port as used by the server
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # internet, tcp
  s.connect((HOST, PORT))
  while 1:
    test_text = raw_input("> ")
    s.sendall(test_text)
    data = s.recv(1024)
    print 'Received', repr(data)
  s.close()

if __name__ == '__main__':
  neromum = Neromum()
  neromum.run()