# nerokid.py

# nerokid.py
#
# one line description
import sys
import os
import time
import subprocess
import shlex
from core import Logger, Socket

INTERVAL = 2.0
LOG_FILES = 'stdout.log', 'stderr.log'


class LogFile(object):

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


class NeroKid(object):
    """The """

    def __init__(self):
        """"""
        self.sock = None
        self.process = None
        self.logger = Logger('KID')
        self.experiment = ' '.join(sys.argv[3:])
        self.log_files = [LogFile(log_file_path) for log_file_path in LOG_FILES]

    def run(self):
        """The Nerokid main."""
        self.logger.log('Kid launched!')
        self.initialize_socket()
        self.logger.log('Launching the experiment...')
        launch_child_process()
        monitor_process()
        logger.log('Process finished!')

    def initialize_socket(self):
        """initialize socket"""
        host, port = sys.argv[1:3]
        port = int(port)
        # Define a socket
        self.sock = Socket(self.logger, host, port)
        self.logger.log('- Mom address: (%s, %d)' % (host, port))
        self.logger.log('- Experiment: %s' % (self.experiment))

    def send_data_to_neromum(self, text):
        """Send status data to Neromum."""
        sock.send_data(text)

    def launch_child_process(self):
        """Launches received script"""
        self.process = subprocess.Popen(shlex.split(self.experiment), universal_newlines=True,
        stdout=open('stdout.log', 'w'), stderr=open('stderr.log', 'w'),
        close_fds=True, bufsize=1)

    def monitor_process(self):
        logger.log('- Experiment PID: %s' % (process.pid))
        while process.poll() == None:
            # Sleep to wait for changes
            time.sleep(INTERVAL)
            collect_new_file_data()

    def collect_new_file_data(self):
        """Collect data what child process outputs"""
        # Check for any new log output
        log_output = {}
        for log_file in self.log_files:
            changes = log_file.read_changes()
            if changes:
                log_output[log_file.path] = changes
        # Send any new log output to Mum
        if log_output:
            sock.send_data({'log_output': log_output})

if __name__ == '__main__':
    NeroKid().run()
