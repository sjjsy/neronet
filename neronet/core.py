# -*- coding: utf-8 -*-
# core.py
#
# Core class and function definitions

import os
import sys
import datetime
import socket
import pickle
import time
import subprocess
import shlex
import copy
import importlib

TIME_OUT = 5.0
"""float: how long the socket waits before failing when sending data
"""

USER_DATA_DIR = '~/.neronet' # Remember to os.path.expanduser
USER_DATA_DIR_ABS = os.path.expanduser(USER_DATA_DIR)
MANDATORY_FIELDS = set(['run_command_prefix', 'main_code_file', 'parameters', 
                        'parameters_format'])
OPTIONAL_FIELDS = set(['outputs', 'output_processor', 'plot', 'collection', 
                        'required_files', 'conditions', 'sbatch_args'])
AUTOMATIC_FIELDS = set(['path', 'time_created', 'time_modified', 'state', 
                        'cluster_id', 'warnings'])

class Cluster(object):
    """ 
    Attributes:
        cid (str): The unique ID (name) of the cluster
        ctype (str): Type of the cluster. Either slurm or unmanaged
        ssh_address (str): SSH address or config hostname corresponding to
            the cluster.
        sbatch_args (str): Slurm SBATCH arguments.
    """

    class Type:
        unmanaged = 'unmanaged'
        slurm = 'slurm'
        _members = set(['slurm', 'unmanaged'])
        @classmethod
        def is_member(cls, arg):
            return arg in cls._members

    def __init__(self, cid, ctype, ssh_address, sbatch_args=None):
        self.cid = cid
        self.ctype = ctype
        self.ssh_address = ssh_address
        self.sbatch_args = sbatch_args
        self.dir = USER_DATA_DIR

    def __str__(self):
        return '%s (%s, %s)' % (self.cid, self.ctype, self.ssh_address)

    def sshrun(self, cmd, inp=None):
        """Execute a shell command via SSH on the remote Neronet cluster."""
        # Ask SSH to execute a command that starts by changing the working
        # directory to 'self.dir' at the machine served at the specified
        # address and port
        scmd = 'ssh %s "cd %s;' % (self.ssh_address, self.dir)
        # Potentially include initialization commands depending on cluster
        # type
        if self.ctype == self.Type.unmanaged:
            pass
        elif self.ctype == self.Type.slurm:
            # Load the python 2.7 module to gain access to the interpreter
            scmd += ' module load python/2.7.4;'
        # Run the given command with the PATH and PYTHONPATH environment
        # variables defined to include the neronet executables and modules
        scmd += ' PATH="%s/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="%s" %s"' \
                % (self.dir, self.dir, cmd)
        # Actual execution
        res = osrunroe(scmd, inp=inp)
        if res.rv != 0:
            msg = ''
            if res.err: msg += '\nErr: %s' % (res.err)
            if res.out: msg += '\nOut: %s' % (res.out)
            raise RuntimeError('Failed to run "%s" via SSH at cluster "%s"!%s'
                % (cmd, self.cid, msg))
        return res
        # PATH="$HOME/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="$HOME/.neronet"

    def test_connection(self):
        res = self.sshrun('python -V')
        if res.rv != 0:
            raise RuntimeError('Failed to run Python via SSH at "%s"!' % (self.cid))
        #TODO: Make version checking smarter
        elif not 'Python 2.7' in res.err:
            raise RuntimeError('Incorrect Python version at "%s": "%s"!' % (self.cid, res.err))
        return True

    def start_neromum(self):
        res = self.sshrun('neromum --start')
        print('Neromum daemon started...')
        #print('Finished: %d, "%s", "%s"' % (res.rv, res.err, res.out))

    def clean_experiments(self, exceptions):
        data = {'action': 'clean_experiments', 'exceptions': exceptions}
        res = self.sshrun('neromum --input', inp=pickle.dumps(data, -1))
        print(res.out)
        if res.err:
            print('Error: %s\n' % (res.err))

    def yield_status(self):
        data = {'action': 'fetch', 'msg': 'I love honeybees!'}
        res = self.sshrun('neromum --input', inp=pickle.dumps(data, -1))
        yield 'Finished: %d, "%s", "%s"' % (res.rv, res.err, res.out)

class Runresult: """A class for holding shell command execution results."""

def osrunroe(cmd, vrb=True, inp=None):
    """Execute a shell command and return the return code, stdout and -err.

    Args:
        vrb (boolean): Whether to print command or not.
        inp (str): Input string for the sub process.

    Returns
        Runresult: The result object of the executed command.
    """
    if vrb: print('> %s' % (cmd))
    if type(cmd) == str:
        cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    res = Runresult()
    res.cmd = cmd
    res.out, res.err = proc.communicate(inp)
    res.rv = proc.poll()
    return res

def osrun(cmd, vrb=True):
    res = osrunroe(cmd, vrb)
    if res.rv != 0:
        raise RuntimeError('osrun(%s) failed! Err: "%s", Out: "%s".' \
                % (res.cmd, res.err, res.out))
    return res

def osrunq(cmd):
    return osrun(cmd, vrb=False)

def get_hostname():
    return osrunq('hostname').out.strip()

def time_now():
    return datetime.datetime.now() #.strftime('%H:%M:%S %d-%m-%Y')

def write_file(filepath, data):
    text = str(data)
    with open(filepath, 'w') as f:
        f.write(text)

def read_file(filepath, default=None):
    result = default
    try:
        with open(filepath, 'r') as f:
            result = ''
            for line in f:
                result += line
    except IOError as e:
        pass
    return result

def import_from(module_name, obj_name):
    """Import object from module, tries to first find module from
    neronet/scripts

    Parameters:
        module (str): name of the module to be imported from
        obj_name (str): name of the object to be imported

    Returns:
        object: The object to be imported
    
    Raises:
        ImportError: If the module to be imported doesn't exist
        AttributeError: If the module doesn't contain an object named obj_name
    """
    try:
        module = importlib.import_module("neronet.scripts." + module_name)
    except Exception as err:
        print '%s\nNeronet failed to process script "%s". Please fix it!' \
                % (err, module_name)
        sys.exit(1)
    return getattr(module, obj_name)

def create_config_template(expid='exp_id', runcmdprefix='python', maincodefile='main.py', *params):
    # Creates a config file with the required fields.
    if os.path.exists('config.yaml'):
        print('A config.yaml file already exists in this folder.')
        return
    with open('config.yaml', 'w') as f:
        f.write('%s:\n' % expid)
        f.write('    run_command_prefix: %s\n' % runcmdprefix)
        f.write('    main_code_file: %s\n' % maincodefile)
        f.write('    parameters:\n')
        if params:
            params_format = ''
            for param in params:
                f.write('        %s:\n' % param)
                params_format += '{%s} ' % param
            f.write("    parameters_format: '%s'\n" % params_format) 
        else:
            f.write('    parameters_format:\n')
        
