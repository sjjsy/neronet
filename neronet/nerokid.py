# -*- coding: utf-8 -*-
"""This module defines Nerokid.

Attributes:
  INTERVAL (float): interval for how long the kid waits until it rechecks
    for changes in the log file
  LOG_FILES (tuple): Log files for stdout and stderr

Example usage:
    ## Unmanaged node example
    python nerokid exp1 --start
    ## Managed node example (Slurm SBATCH)
    #!/bin/sh
    #SBATCH --time=60
    python nerokid exp1 --start
    python nerokid exp1 --launch triton 12345
"""

from __future__ import print_function
import os
import subprocess
import shlex
import time
import sys

import neronet.core
import neronet.daemon
import neronet.neromum

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
    def __init__(self, experiment_id):
        super(Nerokid, self).__init__('nerokid-%s' % (experiment_id))
        self.neromum = None
        self.experiment = neronet.core.ExperimentOLD(experiment_id)
        self.process = None
        self.add_query('launch', self.qry_launch)

    def qry_launch(self, host, port):
        """The Nerokid main.

        Initializes the socket, launches the child process and starts to monitor the child process
        """
        self.neromum = neronet.daemon.QueryInterface(
                neronet.neromum.Neromum(), host=host, port=int(port))
        self.log('Launching a kid...')
        self.log('- Mom address: (%s, %d)' % (self.neromum.host, self.neromum.port))
        self.log('- Experiment ID: "%s"' % (self.experiment.experiment_id))
        self.log_files = [LogFile(log_file_path)
                          for log_file_path in LOG_FILES]
        self.log('Launching the experiment...')
        """Launches received script"""
        self.process = subprocess.Popen(
            shlex.split('sleep 30'),
            universal_newlines=True,
            stdout=open('stdout.log', 'w'),
            stderr=open('stderr.log', 'w'),
            close_fds=True, bufsize=1)
        self.log('- Experiment PID: %s' % (self.process.pid))
        self.experiment.state = 'running'

    def qry_stop(self):
        """Terminate the experiment"""
        if self.process:
            self.process.kill()
            self.log('- Experiment PID: %s terminated' % (self.process.pid))
        super().qry_stop()

    def ontimeout(self):
        """Writes information about the process into a log file on set intervals"""
        if not self.experiment or self.experiment.state != 'running':
            return
        if self.process.poll() == None:
            self.collect_new_file_data()
        else:
            self.experiment.state = 'finished'
            self.refresh_neromum()
            self.qry_stop()

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
            self.experiment.log_output = log_output
            self.refresh_neromum()

    def refresh_neromum(self):
        """Send data to Neromum."""
        self.neromum.query('nerokid_update', self.experiment)

def main():
    """Create a CLI interface object and process CLI arguments."""
    if len(sys.argv) < 2:
        print('Kid experiment ID required!')
        sys.exit(1)
    exp_id = sys.argv[1]
    sys.argv.pop(1)
    #sys.argv = [sys.argv[0]] + sys.argv[2:]
    cli = neronet.daemon.Cli(Nerokid(exp_id))
    cli.parse_arguments()