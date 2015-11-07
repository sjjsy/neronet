# nerokid.py
#
# one line description


import socket

class NeroKid(object):

  def __init__(self, socket, port):
    """"""
    self.socket = socket
    self.port = port
  
  def main(self ):
  	"""The Nerokid main."""
  	pass
  	
  def initialize_socket(self):
    """initialize socket"""
    pass

  def send_data_to_neromum(self ):
  	"""Send status data to Neromum."""  	
    pass
  	
  def launch_child_process(self ):
    """Launches received script"""
    pass
  
  def collect_std_out_data(self):
    """Collect data what child process outputs"""
    pass
  
  def socket_test(self):
  	HOST = '0.0.0.0' # Symbolic name meaning all available interfaces
  	PORT = 50007 # Arbitrary non-privileged port
  	# normal socket with internet and udp, sock_dgram would be tcp
  	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  	s.bind((HOST, PORT)) # binds socket to port
  	s.listen(1) # Listens port or incoming tcp connections
  	conn, addr = s.accept() # Accepts connection and saves handle and address of recipent
  	print 'Connected by', addr
  	while 1:
  	    data = conn.recv(1024) # Conn is the socket we are trying to read data from
  	    if not data: break
  	    conn.sendall(data) # Echoes back the data we received earlier
  	conn.close()
  
if __name__ == '__main__':
	main()