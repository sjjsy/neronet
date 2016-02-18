# -*- coding: utf-8 -*-
""" This module defines the configuration parser for neronet experiment
configuration files and the relating error class
"""

import os
import itertools

import yaml

import neronet.core

EXPERIMENT_CONFIG_FILENAME = 'config.yaml'
NERONET_DIR = os.path.expanduser('~') + '/.neronet/'

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
    def load_config(self, filename, default, check, *args):
        """Loads the yaml file and checks its format

        Parameters:
            filename (str): name of the file to be loaded
            default (dict): default data to be returned and written if the
                file doesn't exist
            check (function): function that checks that the format of the data
                is correct
            args (list): extra arguments for the check function
        
        Returns:
            data (dict): data that was loaded

        Raises:
            FormatError: if the data wasn't correctly formated
        """
        if not os.path.exists(NERONET_DIR):
            os.makedirs(NERONET_DIR)
        if not os.path.exists(NERONET_DIR + filename):
            self.write_yaml(NERONET_DIR + filename, default)
            return default
        data = self.load_yaml(NERONET_DIR + filename)
        check(data, *args)
        return data

    def load_clusters(self, clusters_filename):
        """Loads the clusters file

        Parameters:
            clusters_filename (str): name of the clusters file
        
        Returns:
            dict: data of the clusters

        Raises:
            FormatError: if the data wasn't correctly formated
        """
        cluster_default = {'clusters': {}, 'groups': {}}
        return self.load_config(clusters_filename, cluster_default, 
                                self.check_clusters)

    def check_clusters(self, clusters_data):
        """Checks the format of the cluster data
        
        Parameters:
            clusters_data (dict): data of the clusters

        Raises:
            FormatError: if the data wasn't correctly formated
        """
        errors = []
        clusters = clusters_data.get('clusters', {})
        for cluster_id, fields in clusters.iteritems():
            if 'type' not in fields:
                errors.append('No type specified for cluster "%s"' % cluster_id)
            elif not neronet.core.Cluster.Type.is_member(fields['type']):
                errors.append('Invalid type "%s" for cluster "%s"' % \
                                (fields['type'], cluster_id))
            if 'ssh_address' not in fields:
                errors.append('No ssh address specified for cluster "%s"' % \
                                                            cluster_id)
            if 'sbatch_args' not in fields:
                fields['sbatch_args'] = None

            if not errors:
                clusters[cluster_id] = neronet.core.Cluster(cluster_id,
                        fields['type'], fields['ssh_address'],
                        fields['sbatch_args'])

        groups = clusters_data.get('groups', {})
        for group_name, group_clusters in groups.iteritems():
            for cluster in group_clusters:
                if cluster not in clusters.keys():
                    errors.append('Group "%s" cluster "%s" is not defined' % \
                                    (group_name, cluster))
        if errors:
            raise FormatError(errors)

    def load_preferences(self, preferences_filename, clusters_data):
        """Loads the preferences file
        Parameters:
            preferences_filename (str): name of the preferences file
            clusters_data (dict): data of the clusters

        Returns:
            dict: data of the preferences

        Raises:
            FormatError: if the data wasn't correctly formated
        """
        preferences_default = {'name': '', 'email': '', 'default_cluster': ''}
        return self.load_config(preferences_filename, preferences_default, \
                            self.check_preferences, clusters_data)

    def check_preferences(self, preferences_data, clusters_data):
        """Checks the preferences data

        Parameters:
            preferences_data (dict): data of the preferences
            clusters_data (dict): data of the clusters

        Raises:
            FormatError: if the data wasn't correctly formated
        """
        clusters = clusters_data.get('clusters', {})
        default_cluster = preferences_data['default_cluster']
        if default_cluster not in clusters and default_cluster:
            raise FormatError(['Default cluster %s not defined' % \
                                default_cluster])

    def load_database(self, database_filename):
        """Loads the database file
        
        Parameters:
            database_filename (str): name of the database file

        Returns:
            dict: data of the database
        """
        database_default = {}
        return self.load_config(database_filename, database_default, \
                            self.check_database)

    def check_database(self, database_data):
        pass

    def load_configurations(self, clusters_filename, 
                                    preferences_filename,
                                    database_filename):
        """Loads all the configurations

        Parameters:
            clusters_filename (str): name of the clusters file
            preferences_filename (str): name of the preferences file
            database_filename (str): name of the database file

        Returns:
            tuple of dicts: a tuple containing the data of clusters,
            preferences and database as dicts

        Raises:
            FormatError: if the data wasn't correctly formated
        """
        errors = []
        clusters = {}
        try:
            clusters = self.load_clusters(clusters_filename)
        except FormatError as e:
            errors += e.error_msgs
        try:
            preferences = self.load_preferences(preferences_filename, \
                                                clusters)
        except FormatError as e:
            errors += e.error_msgs
        try:
            database = self.load_database(database_filename)
        except FormatError as e:
            errors += e.error_msgs
        if errors:
            raise FormatError(errors)
        return clusters, preferences, database

    def remove_data(self):
        """Removes the neronet data files
        """
        if os.path.exists(NERONET_DIR):
            os.system('rm -r ' + NERONET_DIR)

    def save_database(self, database_filename, database):
        self.write_yaml(NERONET_DIR + database_filename, database)

    def save_preferences(self, preferences_filename, preferences):
        self.write_yaml(NERONET_DIR + preferences_filename, preferences)

    def save_clusters(self, clusters_filename, clusters):
        cluster_field_dict = {}
        for k, v in clusters['clusters'].items():
            dct = {'type': v.ctype, 'ssh_address': v.ssh_address}
            if v.sbatch_args:
                dct['sbatch_args'] = v.sbatch_args
            cluster_field_dict[k] = dct
        clusters_data = {'clusters': cluster_field_dict,
                'groups': clusters['groups']}
        self.write_yaml(NERONET_DIR + clusters_filename, clusters_data)

    def load_yaml(self, filename):
        """Loads yaml file"""
        with open(filename, 'r') as f:
            data = yaml.load(f.read())
        if not data: data = {}
        return data

    def write_yaml(self, filename, data):
        """Writes a yaml file"""
        with open(filename, 'w') as f:
            f.write(yaml.dump(data, default_flow_style=False))

    def parse_experiments(self, folder):
        """ Parses the configuration file found inside the given folder and
        returns the experiments created as a dictionary.

        Args:
            folder (str): The name of the experiment folder
        
        Returns:
            experiments (dict): Dictionary containing the experiments created
            according to the configuration file in the experiment folder

        Raises:
            IOError: If the folder or configuration file doesn't
            exists

            FormatError: If the configuration file isn't in the correct format
        """

        #Check that the input is valid
        if not os.path.isdir(folder):
            raise IOError('No such folder')
        config_file = os.path.join(folder, EXPERIMENT_CONFIG_FILENAME)
        if not os.path.exists(config_file):
            raise IOError('No config file in folder')
        
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
                        if optional_field == 'conditions':
                            conditions = old_scope[optional_field]
                            for condition in conditions:
                                condition = conditions[condition]
                                cond_errors = \
                                    self.check_conditions(condition) 
                            for err in cond_errors:
                                errors.append(err)
                        new_scope[optional_field] = old_scope[optional_field]

                #Set the folder name as a default collection
                collection = set([os.path.basename(os.path.normpath(folder))])
                if 'collection' in new_scope:
                    c = new_scope['collection']
                    collection = collection | \
                                c if isinstance(c, set) else set([c])
                new_scope['collection'] = collection

                if not errors:
                    #Create the experiments
                    experiment = {}
                    params = []
                    fields = neronet.core.MANDATORY_FIELDS | optional_fields
                    for field in fields:
                        if field == 'parameters':
                            params = \
                                self._param_combinations(new_scope[field])
                        if field == 'conditions':
                            conditions = {}
                            for condition_name in new_scope[field]:
                                condition = new_scope[field][condition_name]
                                condition['name'] = condition_name
                                condition['killvalue'] = float(condition['killvalue'])
                                conditions[condition_name] = \
                                    neronet.core.ExperimentWarning(**condition)
                            experiment[field] = conditions
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

    def check_conditions(self, conditions):
        err = []
        for field in neronet.core.WARNING_FIELDS:
            if field not in conditions:
                err.append("Experiment warning doesn't have field %s" % field)
            elif field == 'when' and 'time' in conditions[field]:
                try:
                    float(conditions[field][4:].strip())
                except:
                    err.append("Invalid syntax at experiment warning 'when' attribute: " + conditions[field])
            elif field == 'killvalue':
                try:
                    float(conditions[field])
                except:
                    err.append("Invalid syntax at experiment warning 'killvalue' attribute")
        return err
            

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
