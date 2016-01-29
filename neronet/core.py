# core.py
#
# Core class and function definitions

import os
import sys
import datetime
import socket
import pickle
import time
#import psutil
from signal import signal, SIGTERM, SIGQUIT
from traceback import print_exc
from copy import deepcopy

TIME_OUT = 5.0
"""float: how long the socket waits before failing when sending data
"""

USER_DATA_DIR = '~/.neronet' # Remember to os.path.expanduser
USER_DATA_DIR_ABS = os.path.expanduser(USER_DATA_DIR)

MANDATORY_FIELDS = set(['run_command_prefix', 'main_code_file', 'parameters', 
                        'parameters_format'])
OPTIONAL_FIELDS = set(['logoutput', 'collection', 'required_files',
                        'conditions'])
AUTOMATIC_FIELDS = set(['path', 'time_created', 'time_modified', 'state', 
                        'cluster'])

class Experiment(object):
    """ 
    Attributes:
        experiment_id (str): Unique identifier to the experiment
        run_command_prefix (str): The run command of the experiment
        main_code_file (str): The code file to be run
        required_files (str): Other files required by the experiments
        logoutput (str): File where the experiment outputs information
        parameters (dict): The Experiment parameters
        parameters_format (str): The format of the experiment parameters
        collection (str): The collection the experiment is part of
        conditions (dict): Special condition for the experiment to do stuff
        state (list of tuples): The states of the experiment with timestamp
        cluster (str): The cluster where the experiment is run
        time_created (str): Timestamp of when the experiment was created
        time_modified (str): Timestamp of when the experiment was modified
        last
        path (str): Path to the experiment folder
    """

    class State:
        none = 'none'
        defined = 'defined'
        submitted = 'submitted'
        submitted_to_kid = 'submitted_to_kid'
        running = 'running'
        finished = 'finished'

    def __init__(self, experiment_id, run_command_prefix, main_code_file,
                    parameters, parameters_format, path, required_files=None,
                    logoutput='output.log', collection=None, conditions=None):
        now = datetime.datetime.now()
        fields = {'run_command_prefix': run_command_prefix,
                    'main_code_file': main_code_file,
                    'required_files': required_files if required_files else [],
                    'logoutput': logoutput,
                    'parameters': parameters,
                    'parameters_format': parameters_format,
                    'collection': collection,
                    'conditions': conditions,
                    'path': path,
                    'time_created': now,
                    'time_modified': now,
                    'states_info': [(Experiment.State.defined, now)],
                    'cluster': None}
        #MAGIC: Creates the attributes for the experiment class
        super(Experiment, self).__setattr__('_fields', fields)
        super(Experiment, self).__setattr__('_experiment_id', experiment_id)
    
    def __getattr__(self, attr):
        """Getter for the experiment class hides the inner dictionary"""
        #Gets the inner dictionary
        fields = super(Experiment, self).__getattribute__('_fields')
        if attr in fields:
            return fields[attr]
        #Gets hidden attributes by adding _
        if attr == 'id':
            attr = 'experiment_id'
        elif attr == 'state':
            return fields['states_info'][-1][0]
        elif attr == 'state_info':
            return fields['states_info'][-1]
        return super(Experiment, self).__getattribute__('_' + attr)

    def __setattr__(self, attr, value):
        """Setter for the experiment class
        
        Raises:
            AttributeError: if the attribute doesn't exist
        """
        #Gets the inner dictionary
        fields = super(Experiment, self).__getattribute__('_fields')
        if attr == 'id' or attr == 'experiment_id':
            super(Experiment, self).__setattr__('_experiment_id', value)
        elif attr in fields or attr in ('log_output', ):
            fields[attr] = value
        else:
            raise AttributeError('Experiment has no attribute named %s' % attr)

    @property 
    def callstring(self):
        rcmd = self._fields['run_command_prefix']
        code_file = self._fields['main_code_file']
        parameters = self._fields['parameters']
        param_format = self._fields['parameters_format']
        parameters_string = param_format.format(**parameters)
        callstring = ' '.join([rcmd, code_file, parameters_string])
        return callstring

    def update_state(self, state):
        """ Updates the state
        """
        self._fields['states_info'].append((state, datetime.datetime.now()))

    def as_dict(self):
        """ Returns the experiment as a dictionary
        """
        return {self._experiment_id: deepcopy(self._fields)}

    def as_gen(self):
        """Creates a generate that generates info about the experiment
        Yields:
            str: A line of experiment status
        """
        yield "%s\n" % self._experiment_id
        yield "  Run command: %s\n" % self._fields['run_command_prefix']
        yield "  Main code file: %s\n" % self._fields['main_code_file']
        params = self._fields['parameters_format'].format( \
            **self._fields['parameters'])
        yield "  Parameters: %s\n" % params
        yield "  Parameters format: %s\n" % self._fields['parameters_format']
        if self._fields['collection']:
            yield "  Collection: %s\n" % self._fields['collection']
        yield "  State: %s\n" % self._fields['state'][-1][0]
        yield "  Last modified: %s\n" % self._fields['time_modified']

    def __str__(self):
        return "%s %s" % (self._experiment_id, self._fields['state'][-1][0])

def osrun(cmd):
    print('> %s' % (cmd))
    os.system(cmd)

def get_hostname():
    return read_file('/etc/hostname').strip()

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

class Logger:

    """A class to simplify logging."""

    def __init__(self, name):
        self.name = name

    def log(self, msg):
        """prints datetime, process name, process message"""
        # Print to stdout in a clear format
        print('%s %s: %s' % (datetime.datetime.now(), self.name, msg))


class Socket:

    """A class to simplify socket usage."""

    def __init__(self, host, port):
        # Save key attributes
        self.host = host
        self.port = port

    def send_data(self, data):
        """Create a socket, send data over it, and close it"""
        # Create a TCP/IP socket
        sock = socket.socket()
        sock.settimeout(TIMEOUT)
        # Connect to the mother
        #self.logger.log('Connecting to (%s, %s)...' % (self.host, self.port))
        sock.connect((self.host, self.port))
        # Send data
        #self.logger.log('Sending data "%s"...' % (data))
        sock.sendall(pickle.dumps(data, -1))
        # Close socket
        #self.logger.log('Closing socket...')
        sock.close()

class ExperimentOLD():
    def __init__(self, experiment_id, path=None, runcmd=None):
        self.experiment_id = experiment_id
        self.path = path
        self.runcmd = runcmd
        self.state = None
        self.log_output = {}
