# -*- coding: utf-8 -*-
""" This module defines the configuration parser for neronet experiment
configuration files and the relating error class
"""

import os
import itertools

import yaml

import neronet.core

CONFIG_FOLDER = os.path.expanduser('~/.neronet')
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

class ConfigManager():
    """ Configuration file parser for neronet configuration files
    """
    def __init__(self, verbosity=0):
        self._verbosity = verbosity
        self._database_file = os.path.join(CONFIG_FOLDER, 'default.yaml')
        self._clusters_file = os.path.join(CONFIG_FOLDER, 'clusters.yaml')
        self._preferences_file = os.path.join(CONFIG_FOLDER, 'preferences.yaml')
        self._load()

    def _load_config(self, config_file, default=None):
        return yaml.load(config_file.read_text()) if config_file.exists() \
                else default

    def _config_loader(self, config_file, default_data):
        data = self._load_config(config_file, default)
        if not data:
            data = default_data
            self._save_config(config_file, data)
        return data

    def _save_config(self, config_file, data):
        """Save config data into the config file path."""
        config_file.write_text(yaml.dump(data, default_flow_style=False))

    def _load(self):
        """
        Load the configurations from the yaml files or creates them if they
        don't exist
        """
        self._load_preferences()
        self._load_clusters()
        self._load_experiments()

    def _load_preferences(self):
        """
        Load the preferences config.
        """
        self.preferences = self._config_loader(self.preferences_file,
            {'name': None, 'email': None, 'default_cluster': None})
        if self._verbosity > 3:
            if 'name' not in self.preferences:
                print('Warning: The user\'s name is not specified')
            if 'email' not in self.preferences:
                print('Warning: The user\'s email is not specified')

    def _load_clusters(self):
        """
        Load the clusters config.
        """
        self.clusters = self._config_loader(self.clusters_file,
            {'clusters': {}, 'groups': None})
        # This checks the format of the clusters file            
        for key, cluster in clusters['clusters'].items():
            if 'type' not in cluster:
                cluster['type'] = 'unmanaged'
            else:
                if cluster['type'] != 'unmanaged':
                    if cluster['type'] != 'slurm':
                        raise FormatError('The cluster type for the cluster ' +
                        key + ' is not valid.')
            if 'port' not in cluster:
                cluster['port'] = 22
            if 'ssh_address' not in cluster:
                raise FormatError('The ssh address for the cluster ' + key + 
                ' is not defined.')
        if self.preferences['default_cluster']:
            if self.preferences['default_cluster'] not in clusters['clusters']:
                raise FormatError('The specified default cluster ' + 
                self.preferences['default_cluster'] +' is not found')

    def _load_experiments(self):
        """
        Load the experiments config.
        """
        self.experiments = self._config_loader(self.experiments_file, {})

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
        experiments = []

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

            #Get the experiment ids from the scope
            definable_fields = neronet.core.MANDATORY_FIELDS | \
                                neronet.core.OPTIONAL_FIELDS
            experiment_ids = set(old_scope) - definable_fields
            for experiment_id in experiment_ids:
                #Initialize the new scope
                new_scope = old_scope[experiment_id]
                missing_mandatory_fields = neronet.core.MANDATORY_FIELDS
                if new_scope:
                    #Check what mandatory fields are missing in the next scope
                    missing_mandatory_fields = missing_mandatory_fields - \
                                                set(new_scope)
                else:
                    new_scope = {}

                #Allows nested experiments to only update certain parameters
                if 'parameters' in new_scope and 'parameters' in old_scope:
                    not_updated = set(old_scope['parameters']) - \
                                    set(new_scope['parameters'])
                    for param in not_updated:
                        new_scope['parameters'][param] = \
                                    old_scope['parameters'][param]

                #Add the missing values from the old scope to the new
                for missing_field in missing_mandatory_fields:
                    if missing_field in old_scope:
                        new_scope[missing_field] = old_scope[missing_field]
                    else:
                        errors.append("Experiment %s missing %s" % \
                                    (experiment_id, missing_field))

                optional_fields = set(old_scope) & neronet.core.OPTIONAL_FIELDS
                for optional_field in optional_fields:
                    if optional_field not in new_scope:
                        new_scope[optional_field] = old_scope[optional_field]
                        

                if not errors:
                    #Create the experiments
                    experiment = {}
                    params = []
                    fields = neronet.core.MANDATORY_FIELDS | optional_fields
                    for field in fields:
                        if field == 'parameters':
                            params = \
                                self._param_combinations(new_scope[field])
                        else:
                            experiment[field] = new_scope[field]

                    experiment['path'] = os.path.abspath(folder)
                    for param in params:
                        experiment['parameters'] = param
                        if len(params) > 1:
                            keys = sorted(param)
                            param_strings = [key + '-' + str(param[key]) for key in keys]
                            name = '_'.join([experiment_id] + param_strings)
                            experiment['experiment_id'] = name
                        else:
                            experiment['experiment_id'] = experiment_id
                        experiments.append(neronet.core.Experiment(**experiment))
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
