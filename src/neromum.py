# neromum.py
#
# 


import socket

class NeroMum(object):

  def __init__(self):
    """Initialize the NeroKid"""
    self.initialize_socket()

  def run(self):
    """The Neromum main.
    Listens for communication from Neroman or Nerokids
    and does as needed. Manages a queue of jobs by the user
    and inputs them to the Warden when there are enough 
    resources."""
    pass

  def initialize_socket(self):
    """Initialize socket"""
    pass

  def save_to_file(self):
    """Save data to the .hdf file"""
    pass

  def start_nerokid(self ):
    """Start a nerokid process on a node"""
    pass
  
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
  
  def ask_nerokid_status(self)
    """see if nerokid is done with the task"""
    pass
  
  def retrieve_nerokid_data(self):
    """if any data, collect it from kid"""
    pass

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