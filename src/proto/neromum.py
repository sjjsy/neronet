# neromum.py

import sys
import socket
import os
import pickle

from core import Logger

logger = Logger('MUM')

# Parse arguments
experiment = ' '.join(sys.argv[1:])
# Create a TCP/IP socket
logger.log('Creating the socket')
sock = socket.socket()
sock.settimeout(5.0)
# Bind the socket to localhost, auto choose port
sock.bind(('localhost', 0))
# Put the socket into server mode
sock.listen(1)
# Retrieve socket specs
host, port = sock.getsockname()
# Launch the kid
logger.log('Launching kids')
os.system('python3.5 nerokid.py %s %d %s &' % (host, port, experiment))
# Start receive loop
logger.log('Starting receive loop')
while True:
    # wait for a connection
    logger.log('Waiting for connection...')
    try:
        con, (khost, kport) = sock.accept()
    except socket.timeout:
        logger.log('- receive timeout...')
        continue
    #logger.log('Connection from (%s, %d)' % (khost, kport))
    # Receive the data in small chunks and retransmit it
    data = b''
    while True:
        #logger.log('Receiving data...')
        chunk = con.recv(4096) # 16, 4096
        if chunk:
            data += chunk
        else:
            break
    # Clean up the connection
    con.close()
    # Process data
    if data:
        data = pickle.loads(data)
        #logger.log('Received "%s"' % (data))
        if type(data) == dict:
            if 'log_output' in data:
                for log_path, new_text in data['log_output'].items():
                    logger.log('New output in %s:' % (log_path))
                    for ln in new_text.split('\n'):
                        if not ln: continue
                        logger.log('    %s' % (ln.strip()))
            elif 'state' in data:
                if data['state'] == 'STARTED':
                    logger.log('Kid has started!')
                elif data['state'] == 'FINISHED':
                    logger.log('Kid has finished!')
                    break
# Shutdown the socket
logger.log('Shutting down')
sock.shutdown(socket.SHUT_RDWR)