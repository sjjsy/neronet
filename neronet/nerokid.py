# -*- coding: utf-8 -*-
"""This module defines Nerokid.

Attributes:
  INTERVAL (float): interval for how long the kid waits until it rechecks
    for changes in the log file
  LOG_FILES (tuple): Log files for stdout and stderr
"""
import sys
import os
import time
import subprocess
import shlex

import neronet.core
import neronet.daemon

INTERVAL = 2.0
LOG_FILES = 'stdout.log', 'stderr.log'
packet = {"running": True, "log_output": ""}
commands = ("status")

class LogFile(object):

    """A class that facilitates efficient monitoring of logfile changes."""

    def __init__(self, path):
        """Create a LogFile object to represent a log file.

        Args:
            path (str): the file path to the log file.
        """
        self.path = path
        self.rtime = 0
        self.seek = 0

    def read_changes(self):
        """Read changes made to the logfile."""
        mtime = os.stat(self.path).st_mtime
        if mtime > self.rtime:
            self.rtime = mtime
            with open(self.path, 'r') as stream:
                stream.seek(self.seek)
                changes = stream.read()
                self.seek = stream.tell()
                return changes


class Nerokid(neronet.daemon.Daemon):

    """A class to specify the Nerokid object.

    Runs in a cluster node and manages and monitors the experiment given.

    Gets host as the 1st command line argument
    Port as the 2nd
    Experiment as the 3rd
    Experiment parameters from 4th argument onwards
    """
    def __init__(self):
        super().__init__('nerokid')
        self.sock = None
        self.process = None
        self.add_query('launch', self.qry_launch)

    def qry_launch(self, host, port, experiment_id):
        """The Nerokid main.

        Initializes the socket, launches the child process and starts to monitor the child process
        """
        self.log('Kid launched!')
        self.experiment_id = experiment_id
        self.log_files = [LogFile(log_file_path)
                          for log_file_path in LOG_FILES]
        # Define a socket
        self.sock = neronet.core.Socket(host, int(port))
        self.log('- Mom address: (%s, %d)' % (self.sock.host, self.sock.port))
        self.log('- Experiment ID: %s' % (self.experiment_id))
        self.log('Launching the experiment...')
        self.launch_child_process()
        self.monitor_process()
        self.log('Process finished!')

    def qry_stop(self):
        """Terminate the experiment"""
        if self.process:
            self.process.kill()
            self.log('- Experiment PID: %s terminated' % (self.process.pid))
        super().qry_stop()

    def launch_child_process(self):
        """Launches received script"""
        self.process = subprocess.Popen(
            shlex.split('sleep 30'),
            universal_newlines=True,
            stdout=open('stdout.log', 'w'),
            stderr=open('stderr.log', 'w'),
            close_fds=True, bufsize=1)

    def monitor_process(self):
        """Writes information about the process into a log file on set intervals"""
        self.log('- Experiment PID: %s' % (self.process.pid))
        packet["running"] = True
        while self.process.poll() == None:
            # Sleep to wait for changes
            time.sleep(INTERVAL)
            self.collect_new_file_data()
        packet["running"] = False
        self.send_data_to_neromum(packet)

    def send_data_to_neromum(self, text):
        """Send status data to Neromum."""
        self.sock.send_data(text)

    def collect_new_file_data(self):
        """Collect any data that the child process outputs and send them to neromum"""
        # Check for any new log output
        log_output = {}
        for log_file in self.log_files:
            changes = log_file.read_changes()
            if changes:
                log_output[log_file.path] = changes
        # Send any new log output to Mum
        if log_output:
            packet["log_output"] = log_output
            self.send_data_to_neromum(packet)

class NerokidCli(neronet.daemon.Cli):
    def __init__(self):
        super().__init__(Nerokid())
        self.funcs.update({
            'launch': self.func_launch,
        })

    def func_launch(self, *pargs, **kwargs):
        self.query('launch', *pargs, **kwargs)

def main():
    """Create a Nerokid and call its run method."""
    cli = NerokidCli()
    cli.parse_arguments()