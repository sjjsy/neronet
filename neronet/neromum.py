# neromum.py
#
# python3.5 neromum.py python3.5 sleep.py 20 0.5

import sys
import socket
import os
import pickle
import select

from core import Logger


#need database parsing

class Neromum(object):

    def __init__(self):
        self.sock = None
        self.experiment = ' '.join(sys.argv[1:])
        self.logger = Logger('MUM')
        self.running = True
        self.open_incoming_connections = []
        self.open_outgoing_connections = []

    def run(self):

        self.logger.log('Creating the socket')
        self.initialize_socket()
        self.send_experiment_to_node()
        self.start_nerokid()
        #self.start_nerokid2()
        self.listen_loop()
        self.logger.log('Shutting down')
        sock.shutdown(socket.SHUT_RDWR)



    def initialize_socket(self):
        self.sock = socket.socket()
        self.sock.settimeout(5.0)
        # Bind the socket to localhost, auto choose port
        self.sock.bind(('localhost', 0))
        # Put the socket into server mode
        self.sock.listen(1)
        # Retrieve socket specs
        self.host, self.port = self.sock.getsockname()
        self.open_incoming_connections.append(self.sock)

    def save_to_file(self, data, file):
        pass

    def start_nerokid(self):
        self.logger.log('Launching kids')
        os.system('ssh localhost python3 nerokid.py %s %d %s &' % (self.host, self.port, self.experiment))

    def send_data_to_neroman(self):
        pass

    def send_experiment_to_node(self):
        os.system('scp sleep.py core.py nerokid.py localhost:~/')

    def kill_child(self):
        pass

    def ask_slurm_for_free_node(self):
        pass

    #yup, evrything below needs complete rewrite.
    def get_nerokid_connection(self):
        self.logger.log('Waiting for kid connection...')
        try:
            self.kid_con, (khost, kport) = self.sock.accept()
        except socket.timeout:
            self.logger.log('- receive timeout...')
            return False
        return True

    def get_data_from_nerokid(self):
        # wait for a connection

        # Receive the data in small chunks and retransmit it
        self.data = b''
        while True:
            chunk = self.kid_con.recv(4096)  # 16, 4096
            if chunk:
                self.data += chunk
            else:
                break
        # Clean up the connection
        self.kid_con.close()

    def parse_nerokid_data(self):
        if self.data:
            self.data = pickle.loads(self.data)
            if type(self.data) == dict:
                if 'log_output' in self.data:
                    for log_path, new_text in self.data['log_output'].items():
                        self.logger.log('New output in %s:' % (log_path))
                        for ln in new_text.split('\n'):
                            if not ln:
                                continue
                            self.logger.log('    %s' % (ln.strip()))
                elif 'state' in self.data:
                    if self.data['state'] == 'STARTED':
                        self.logger.log('Kid has started!')
                    elif self.data['state'] == 'FINISHED':
                        self.logger.log('Kid has finished!')
                        return

    def listen_loop(self):
        while True:
            inRdy,outRdy ,excpRdy = select.select(self.open_incoming_connections, [],[])
            for s in inRdy:
                if s == self.sock:
                    client, address = s.accept() 
                    self.open_incoming_connections.append(client) 
                    print('new client added%s'%str(address)) 
                else:
                    self.data = s.recv(4096)
                    if self.data:
                        self.parse_nerokid_data()
                    else:
                        s.close()
                        self.open_incoming_connections.remove(s)



if __name__ == '__main__':
    Neromum().run()