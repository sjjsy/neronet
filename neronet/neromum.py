# -*- coding: utf-8 -*-
"""This module defines Neromum.
"""

# TODO: need database parsing

import sys
import pickle

import neronet.core
import neronet.daemon
import neronet.nerokid

class Neromum(neronet.daemon.Daemon):

    """A class to specify the Neromum object.

    Runs in the cluster and manages and monitors all the nodes.

    Gets the experiment as the 1st command line argument
    Experiment parameters from 2nd onwards.

    Attrs:
        exp_dict (dict): A dict of all experiments submitted to this mum by
            experiment ID.
    """

    def __init__(self):
        super().__init__('neromum')
        self.exp_dict = {}
        self.add_query('experiment', self.qry_exp)
        self.add_query('list_exps', self.qry_list_exps)
        self.add_query('exp_update', self.qry_exp_update)

    def qry_exp(self):
        """Receive a new experiment job from Neroman."""
        # TODO: read experiment object from stdin
        exp = Experiment(experiment_id='exp1', run_command_prefix='python',
                main_code_file='main.py', parameters=['4', '3'],
                parameters_format='%d %d',
                path='/home/smarisa/snc/pro/neronet/test/experiments/sleep',
                required_files=None, logoutput='out', collection=None,
                conditions=None)
        exp.update_state(neronet.core.Experiment.State.submitted)
        self.exp_dict[exp.id] = exp
        self._reply['rv'] = 0

    def qry_list_exps(self):
        """List all experiments submitted to this mum."""
        msg = 'Experiments:\n'
        for exp in self.exp_dict.values():
            msg += '- %s  %s\n' % (exp.id, exp.path)
        self._reply['msgbody'] = msg
        self._reply['rv'] = 0

    def qry_exp_update(self, changes):
        """Extract information from Nerokids' data updates."""
        exp = self.exp_dict[experiment.id]
        for log_path, new_text in experiment.log_output.items():
            self.log('New output in %s:' % (log_path))
            for ln in new_text.split('\n'):
                if not ln:
                    continue
                self.log('    %s' % (ln.strip()))
        exp.state = experiment.state
        if exp.state == 'finished':
            self.log('Kid %s has finished!' % (exp.experiment_id))
        self._reply['rv'] = 0

    def ontimeout(self):
        for exp in self.exp_dict.values():
            if exp.state == neronet.core.Experiment.State.submitted:
                self.start_exp(exp)
                return # pace submission by launching one at a time

    def start_exp(self, exp):
        """Starts the exp in the unmanaged node."""
        self.log('Launching kid %s...' % (exp.id))
        nerokid = neronet.daemon.QueryInterface(neronet.nerokid.Nerokid(exp.id))
        nerokid.start()
        nerokid.query('launch', self.host, self.port)
        #neronet.core.osrun('nerokid --start')
        #neronet.core.osrun('nerokid --query launch %s %d %s'
        #    % (self.host, self.port, nerokid.experiment_id))
        exp.state = 'running'

class NeromumCli(neronet.daemon.Cli):
    def __init__(self):
        super().__init__(Neromum())
        self.funcs.update({
            'input' : self.func_input,
        })

    def func_input(self):
        data = input()
        print('Data:\n%s\n' % (data))
        while(not ("***" in data)):
            data = input("") # pickle.loads()
            print('Data:\n%s\n' % (data))
        #data = sys.stdin.readLine() # pickle.loads()
        #print('Data:\n%s\n' % (data))
        #nerokid_dqi = neronet.daemon.QueryInterface(neronet.nerokid.Nerokid('test'))
        #nerokid_dqi.start()
        #nerokid_dqi = neronet.daemon.QueryInterface(neronet.nerokid.Nerokid('test'))
        #print(nerokid_dqi.query('status'))
        #data = sys.stdin.read() # pickle.loads()
        #print('Data:\n%s\n' % (data))

def main():
    """Create a CLI interface object and process CLI arguments."""
    cli = NeromumCli()
    cli.parse_arguments()
