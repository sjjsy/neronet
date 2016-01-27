# -*- coding: utf-8 -*-
"""This module defines Neromum.
"""

# TODO: need database parsing

import sys
import pickle
import glob

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
        super(Neromum, self).__init__('neromum')
        self.exp_dict = {}
        self.add_query('list_exps', self.qry_list_exps)
        self.add_query('exp_update', self.qry_exp_update)

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
        # Load all experiments into the dict that have not yet been loaded
        for exp_file in glob.glob('./experiments/*/exp.pickle'):
            exp_id = os.path.basename(os.path.dirname(exp_file))
            if exp_id not in self.exp_dict:
                self.log('New experiment submitted: %s...' % (exp_id))
                exp = pickle.loads(neronet.core.read_file(exp_file))
                self.exp_dict[exp_id] = exp
        # Start an experiment if there is any to start
        for exp in self.exp_dict.values():
            if exp.state == neronet.core.Experiment.State.submitted:
                # TODO: Allow sbatch launch
                # Launch experiment in the local (umanaged) node
                self.log('Launching experiment %s...' % (exp.id))
                nerokid = neronet.daemon.QueryInterface(neronet.nerokid.Nerokid(exp.id))
                nerokid.start()
                nerokid.query('launch', self.host, self.port)
                return # pace submission by launching one at a time

class NeromumCli(neronet.daemon.Cli):
    def __init__(self):
        super(NeromumCli, self).__init__(Neromum())
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

#if __name__ == '__main__':
#    main()