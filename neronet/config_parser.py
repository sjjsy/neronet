# -*- coding: utf-8 -*-
""" This module defines the configuration parser for neronet experiment
configuration files and the relating error class
"""

import datetime
import os
import itertools

import yaml

CONFIG_FILENAME = 'config.yaml'

class FormatError(Exception):
    """ Exception raised when experiment config file is poorly formatted
    """

    def __init__(self, error_msgs):
        """
        Args:
            error_msgs (list): List of error messages
        """
        self.error_msgs = error_msgs

    def __str__(self):
        return '\n'.join([''] + self.error_msgs)

class ConfigParser():
    """ Configuration file parser for neronet configuration files
    """
    def _time_now(self):
        """ A helper function to save the current time in consistend format

        Return:
            The current time as a string
        """
        return datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')

    def parse_experiments(self, folder):
        """ Parses the configuration file found inside the given folder and
        returns the experiments created as a dictionary.

        Args:
            folder (str): The name of the experiment folder
        
        Returns:
            experiments (dict): Dictionary containing the experiments created
            according to the configuration file in the experiment folder

        Raises:
            FileNotFoundError: If the folder or configuration file doesn't
            exists

            FormatError: If the configuration file isn't in the correct format
        """

        #Check that the input is valid
        if not os.path.isdir(folder):
            raise FileNotFoundError('No such folder')
        config_file = os.path.join(folder, CONFIG_FILENAME)
        if not os.path.exists(config_file):
            raise FileNotFoundError('No config file in folder')
        
        if os.stat(config_file).st_size == 0:
            raise FormatError(['Empty config file'])
        
        with open(config_file, 'r') as file:
            data = yaml.load(file.read())

        return self.parse_experiment_data(folder, data)
        
    def parse_experiment_data(self, folder, data):
        """ Parses experiment configuration data to experiments

        Args:
            data (dict): Experiment configuration data

        Returns:
            experiments (dict): Dictionary containing all the experiments made
            from the data
        Raises:
            FormatError: If the configuration file isn't in the correct format
        """
        errors = []
        experiments = {}

        def _read_experiments(old_scope):
            """ A nested helper function to recursively read the experiment
            configuration data

            Args:
                old_scope (dict): the previous scope of the iteration.
                Contains the current old scope of the fields and the new
                scopes as the experiment ids.

            Raises:
                FormatError: if the configuration file format is incorrect.
                Lists all found errors.
            """

            fields = ['run_command_prefix', 'main_code_file',
                'parameters', 'parameters_format', 'logoutput',
                'collection']
            
            #Get the experiment ids from the scope
            experiment_ids = set(old_scope) - set(fields)
            for experiment_id in experiment_ids:
                #Initialize the new scope
                new_scope = old_scope[experiment_id]
                
                if new_scope:
                    #Check what fields are missing in the next scope
                    missing_fields = set(fields) - set(old_scope[experiment_id])
                else:
                    new_scope = {}
                    missing_fields = set(fields)

                #Allows nested experiments to only update certain parameters
                if 'parameters' in new_scope and 'parameters' in old_scope:
                    not_updated = set(old_scope['parameters']) - \
                                    set(new_scope['parameters'])
                    for param in not_updated:
                        new_scope['parameters'][param] = \
                                    old_scope['parameters'][param]
                if new_scope:
                    #Check what fields are missing in the next scope
                    missing_fields = set(fields) - set(old_scope[experiment_id])
                else:
                    new_scope = {}
                    missing_fields = set(fields)
                
                #Add the missing values from the old scope to the new
                for missing_field in missing_fields:
                    if missing_field in old_scope:
                        new_scope[missing_field] = old_scope[missing_field]
                    else:
                        errors.append("Experiment %s missing %s" % \
                                    (experiment_id, missing_field))
                
                if not errors:
                    #Create the experiments
                    experiment = {}
                    params = []
                    for field in fields:
                        if field == 'parameters':
                            params = \
                                self._param_combinations(new_scope[field])
                        else:
                            experiment[field] = new_scope[field]
                    experiment['cluster'] = None
                    experiment['time_created'] = self._time_now()
                    experiment['state'] = \
                                [['defined', experiment['time_created']]]
                    experiment['time_modified'] = experiment['time_created']
                    experiment['path'] = os.path.abspath(folder)
                    for param in params:
                        experiment['parameters'] = param
                        if len(params) > 1:
                            keys = sorted(param)
                            param_strings = [key + '-' + str(param[key]) for key in keys]
                            name = '_'.join([experiment_id] + param_strings)
                            #Create copies of the dicts
                            experiments[name] = dict(experiment)
                        else:
                            experiments[experiment_id] = experiment
                _read_experiments(new_scope)
        
        _read_experiments(data)

        if errors:
            raise FormatError(errors)
        if experiments:
            return experiments
        else:
            raise FormatError(['No experiments defined in config file'])

    def _param_combinations(self,params):
        """ A helper function to create all combinatorial subsets of the value
        lists

        Args:
            params (dict): dictionary containing the variable names as keys and the
            values as single value or lists. Single values will be converted to lists.

        Return:
            param_combinations (list of dicts): List of all combinatorial
            subsets as dicts of the keys (variable names).

        """
        values = params.values()
        
        #Horrific, type checking!
        values = [value if isinstance(value, list) else [value] \
                        for value in values]
        keys = params.keys()
        #Creates all the combinatorial subsets
        value_combinations = list(itertools.product(*values))
        
        #Maps the values to the keys
        param_combinations = [dict(zip(keys, values)) \
                                for values in value_combinations]
        return param_combinations
