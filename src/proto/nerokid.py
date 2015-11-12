# nerokid.py

import sys
import os
import time
import subprocess
import shlex

from core import Logger, Socket

INTERVAL = 1.0
LOG_FILES = 'stdout.log', 'stderr.log'

class LogFile:
    def __init__(self, path):
        self.path = path
        self.rtime = 0
        self.seek = 0
    def read_changes(self):
        mtime = os.stat(self.path).st_mtime
        if mtime > self.rtime:
            self.rtime = mtime
            with open(self.path, 'r') as stream:
                stream.seek(self.seek)
                changes = stream.read()
                self.seek = stream.tell()
                return changes

# Define log files
log_files = [LogFile(log_file_path) for log_file_path in LOG_FILES]
# Define a logger
logger = Logger('KID')
logger.log('Kid launched!')
# Parse arguments
host, port = sys.argv[1:3]
experiment = ' '.join(sys.argv[3:])
port = int(port)
# Define a socket
sock = Socket(logger, host, port)
# Display basic info
logger.log('- Mom address: (%s, %d)' % (host, port))
logger.log('- Experiment: %s' % (experiment))
# Start the experiment
logger.log('Launching the experiment...')
process = subprocess.Popen(shlex.split(experiment), universal_newlines=True,
    stdout=open('stdout.log', 'w'), stderr=open('stderr.log', 'w'),
    close_fds=True, bufsize=1)
logger.log('- Experiment PID: %s' % (process.pid))
# Notify Mum of having started the experiment
sock.send_data({'state': 'STARTED'})
# Start the experiment monitoring loop
while process.poll() == None:
    # Sleep to wait for changes
    time.sleep(INTERVAL)
    # Check for any new log output
    log_output = {}
    for log_file in log_files:
        changes = log_file.read_changes()
        if changes:
            #logger.log('Output in %s: %s' % (log_file.path, changes))
            log_output[log_file.path] = changes
    # Send any new log output to Mum
    if log_output:
        sock.send_data({'log_output': log_output})
logger.log('Process finished!')
# Send state update to Mum
sock.send_data({'state': 'FINISHED', 'returncode': process.returncode})