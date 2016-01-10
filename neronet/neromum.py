# -*- coding: utf-8 -*-
"""This module defines Neromum.
"""

# TODO: need database parsing

import sys
import socket
import os
import pickle
import select

import neronet.core
import neronet.daemon

class Neromum(neronet.daemon.Daemon):

    """A class to specify the Neromum object.

    Runs in the cluster and manages and monitors all the nodes.

    Gets the experiment as the 1st command line argument
    Experiment parameters from 2nd onwards.
    """

    def __init__(self):
        super().__init__('neromum')
        self.nerokid_queue = []
        self.nerokid_dict = {}
        self.add_query('nerokid', self.qry_nerokid)
        self.add_query('list_nerokids', self.qry_list_nerokids)
        self.add_query('nerokid_update', self.qry_nerokid_update)

    def qry_nerokid(self, experiment_id, path, runcmd):
        nerokid = neronet.core.Experiment(experiment_id, path, runcmd)
        self.nerokid_queue.append(nerokid)
        self.nerokid_dict[experiment_id] = nerokid
        self._reply['rv'] = 0

    def qry_list_nerokids(self):
        msg = 'Nerokids:\n'
        for nerokid in self.nerokid_queue:
            msg += '- %s' % (nerokid.experiment_id)
        self._reply['msgbody'] = msg
        self._reply['rv'] = 0

    def qry_nerokid_update(self, experiment_id, state, log_output):
        """Extract information from nerokid's data updates."""
        nerokid = self.nerokid_dict[experiment_id]
        for log_path, new_text in log_output.items():
            self.log('New output in %s:' % (log_path))
            for ln in new_text.split('\n'):
                if not ln:
                    continue
                self.log('    %s' % (ln.strip()))
        nerokid.state = state
        if nerokid.state == 'finished':
            self.log('Kid %s has finished!' % (nerokid.experiment_id))
        self._reply['rv'] = 0

    def ontimeout(self):
        for nerokid in self.nerokid_queue:
            if nerokid.state == None:
                self.start_nerokid(nerokid)
                return

    def start_nerokid(self, nerokid):
        """Starts the nerokid in the node"""
        self.log('Launching kid %s...' % (nerokid.experiment_id))
        neronet.core.osrun('nerokid --start')
        neronet.core.osrun('nerokid --launch %s %d %s'
            % (self.host, self.port, nerokid.experiment_id))
        nerokid.state = 'running'

class NeromumCli(neronet.daemon.Cli):
    def __init__(self):
        super().__init__(Neromum())

def main():
    """Create a Neromum and call its run method."""
    cli = NeromumCli()
    cli.parse_arguments()
