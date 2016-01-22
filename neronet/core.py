# core.py
#
# Core class and function definitions

from __future__ import print_function
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

MANDATORY_FIELDS = set(['run_command_prefix', 'main_code_file', 'parameters', 
                        'parameters_format'])
OPTIONAL_FIELDS = set(['logoutput', 'collection', 'required_files',
                        'conditions'])
AUTOMATIC_FIELDS = set(['path', 'time_created', 'time_modified', 'state', 
                        'cluster'])

class Experiment:
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
    def __init__(self, experiment_id, run_command_prefix, main_code_file,
                    parameters, parameters_format, path, required_files=[],
                    logoutput='output.log', collection=None, conditions=None):
        self._experiment_id = experiment_id
        now = datetime.datetime.now()
        self._fields = {'run_command_prefix': run_command_prefix,
                        'main_code_file': main_code_file,
                    'required_files': required_files,
                    'logoutput': logoutput,
                    'parameters': parameters,
                    'parameters_format': parameters_format,
                    'collection': collection,
                    'conditions': conditions,
                    'path': path,
                    'time_created': now,
                    'time_modified': now,
                    'state': [['defined', now]],
                    'cluster': None}
    
    @property
    def id(self):
        return self._experiment_id

    @id.setter
    def id(self, value):
        self._experiment_id = value
    
    @property
    def run_command_prefix(self):
        self._fields['run_command_prefix']
    
    @run_command_prefix.setter
    def run_command_prefix(self, value):
        self._fields['run_command_prefix'] = value
    @property
    def main_code_file(self):
        return self._fields['main_code_file']
    
    @main_code_file.setter
    def main_code_file(self, value):
        self._fields['main_code_file'] = value

    @property
    def parameters(self):
        return self._fields['parameters']
    
    @parameters.setter
    def parameters(self, value):
        self._fields['parameters'] = value
     
    @property
    def parameters_format(self):
        return self._fields['parameters_format']
    
    @parameters_format.setter
    def parameters_format(self, value):
        self._fields['parameters_format'] = value
 
    @property
    def logoutput(self):
        return self._fields['logoutput']
    
    @logoutput.setter
    def logoutput(self, value):
        self._fields['logoutput'] = value
     
    @property
    def collection(self):
        return self._fields['collection']
    
    @collection.setter
    def collection(self, value):
        self._fields['collection'] = value
     
    @property
    def required_files(self):
        return self._fields['required_files']
    
    @required_files.setter
    def required_files(self, value):
        self._fields['required_files'] = value
     
    @property
    def conditions(self):
        return self._fields['conditions']
    
    @conditions.setter
    def conditions(self, value):
        self._fields['conditions'] = value
     
    @property
    def cluster(self):
        return self._fields['cluster']
    
    @cluster.setter
    def cluster(self, value):
        self._fields['cluster'] = value
     
    @property
    def path(self):
        return self._fields['path']
    
    @path.setter
    def path(self, value):
        self._fields['path'] = value
     
    @property
    def time_created(self):
        return self._fields['time_created']
    
    @property
    def time_modified(self):
        return self._fields['time_modified']
    
    @time_modified.setter
    def time_modified(self, value):
        self._fields['time_modified'] = value
     
    @property
    def state(self):
        return self._fields['state'][-1]
    
    @property
    def states(self):
        return self._fields['state']

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
        self._fields['state'].append([state, datetime.datetime.now()])

    def as_dict(self):
        """ Returns the experiment as a dictionary
        """
        return {self._experiment_id: deepcopy(self._fields)}

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
