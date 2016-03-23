# -*- coding: utf-8 -*-
""" This module defines the configuration parser for neronet experiment
configuration files and the relating error class
"""

import os
import itertools

import yaml

import neronet.core
import neronet.cluster
import neronet.experiment

EXPERIMENT_CONFIG_FILENAME = 'config.yaml'

class FormatError(Exception):
    """ Exception raised when experiment config file is poorly formatted
    """

    def __init__(self, error_msgs):
        """
        Parameters:
            error_msgs (list): List of error messages
        """
        self.error_msgs = error_msgs if isinstance(error_msgs, list) \
                                        else [error_msgs]

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
        if not os.path.exists(neronet.core.USER_DATA_DIR_ABS):
            os.makedirs(neronet.core.USER_DATA_DIR_ABS)
        if not os.path.exists(os.path.join(neronet.core.USER_DATA_DIR_ABS, \
                                filename)):
            self.write_yaml(os.path.join(neronet.core.USER_DATA_DIR_ABS, \
                                filename), default)
            return default
        data = self.load_yaml(os.path.join(neronet.core.USER_DATA_DIR_ABS, \
                            filename))
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
                errors.append('%s: no type specified for cluster' \
                                % cluster_id)
            elif not neronet.cluster.Cluster.Type.is_member(fields['type']):
                errors.append('%s: invalid type "%s" for cluster' % \
                                (cluster_id, fields['type']))
            if 'ssh_address' not in fields:
                errors.append('%s: no ssh address specified for cluster' \
                                % cluster_id)
            if 'sbatch_args' not in fields:
                fields['sbatch_args'] = None

            if not errors:
                clusters[cluster_id] = neronet.cluster.Cluster(cluster_id,
                        fields['type'], fields['ssh_address'],
                        fields['sbatch_args'])

        groups = clusters_data.get('groups', {})
        for group_name, group_clusters in groups.iteritems():
            for cluster in group_clusters:
                if cluster not in clusters.keys():
                    errors.append('%s: cluster "%s" is not defined for group' % \
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
            raise FormatError(['default cluster %s  is not defined' % \
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

    def save_database(self, database_filename, database):
        self.write_yaml(os.path.join(neronet.core.USER_DATA_DIR_ABS, \
                        database_filename), database)

    def save_preferences(self, preferences_filename, preferences):
        self.write_yaml(os.path.join(neronet.core.USER_DATA_DIR_ABS, \
                        preferences_filename), preferences)

    def save_clusters(self, clusters_filename, clusters):
        cluster_field_dict = {}
        for k, v in clusters['clusters'].items():
            dct = {'type': v.ctype, 'ssh_address': v.ssh_address, 'average_load': v.average_load}
            if v.sbatch_args:
                dct['sbatch_args'] = v.sbatch_args
            cluster_field_dict[k] = dct
        clusters_data = {'clusters': cluster_field_dict,
                'groups': clusters['groups']}
        self.write_yaml(os.path.join(neronet.core.USER_DATA_DIR_ABS, \
                        clusters_filename), clusters_data)

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
            raise IOError('no such folder')
        config_file = os.path.join(folder, EXPERIMENT_CONFIG_FILENAME)
        if not os.path.exists(config_file):
            raise IOError('no config file in folder')
        
        if os.stat(config_file).st_size == 0:
            raise FormatError(['empty config file'])
        
        with open(config_file, 'r') as file:
            data = yaml.load(file.read())

        return self.parse_experiment_data(folder, data)
        
    def parse_experiment_data(self, folder, data):
        """ Parses experiment configuration data to experiments

        Parameters:
            data (dict): Experiment configuration data

        Returns:
            experiments (list): List containing all the experiments made from 
            the data
        Raises:
            FormatError: If the configuration file isn't in the correct format
        """
        errors = []
        experiments = []
        definable_fields = neronet.experiment.MANDATORY_FIELDS | \
                            neronet.experiment.OPTIONAL_FIELDS

        def _check_experiment_data(data):
            """ Horrible helper function riddled with type checking, yaml
            doesn't have a configurable schema to allow easy type checking :(
            """
            exp_id = data['experiment_id']
            
            def check_type(field, t):
                """Checks that the field is certain type, horrid
                """
                types = {"string": str, "dict": dict, "list": list}
                if not isinstance(data[field], types[t]):
                    errors.append("%s: %s should be a %s" % \
                                    (exp_id, field, t))
                    return False
                return True

            #Check the mandatory experiment parameters
            if 'run_command_prefix' not in data:
                 errors.append("%s: run_command_prefix not defined" % \
                                exp_id)
            else:
                check_type('run_command_prefix', 'string')

            if 'main_code_file' not in data:
                 errors.append("%s: main_code_file not defined" % \
                                exp_id)
            else:
                if check_type('main_code_file', 'string'):
                    main_code_file = data['main_code_file']
                    filepath = os.path.join(folder, main_code_file)
                    
                    #Check that the main code file exists
                    if not os.path.exists(filepath):
                        errors.append("%s: no file named %s in folder %s" % \
                                    (exp_id, main_code_file, folder))
            
            if 'parameters' in data:
                if check_type('parameters', 'dict'):
                    if 'parameters_format' not in data:
                        errors.append("%s: parameters format not defined for"
                                        "parameters" % exp_id)

            #Check the optional experiment parameters
            if 'parameters_format' in data:
                if check_type('parameters_format', 'string'):
                    if 'parameters' not in data:
                        errors.append("%s: parameters not defined for"
                                        "parameters format" % exp_id)
                    else:
                        #Check that the parameters fit the format
                        try:
                            pformat = data['parameters_format']
                            pformat.format(**data['parameters'])
                        except:
                            errors.append("%s: cannot format parameters"
                                " according to parameters format" % exp_id)
            if 'outputs' in data: 
                check_type('outputs', 'list')
            if 'output_line_processor' in data:
                check_type('output_line_processor', 'dict')
                for output_file, pstring in \
                        data['output_line_processor'].items():
                    if 'outputs' in data and \
                        output_file not in data['outputs']:
                        errors.append("%s: no output file named %s defined in"
                                " outputs for output line processor" \
                                % exp_id)
                    try:
                        plist = pstring.split()
                        module = plist[0]
                        function = plist[1]
                    except:
                        errors.append("%s: couldn't get module or function"
                                    " from output line processor arguments" \
                                    % exp_id)
                    if not neronet.core.can_import(module, function):
                        errors.append("%s: can't import %s from %s" 
                                        " for output line processor" \
                                        % (exp_id, module, function))
            if 'output_file_processor' in data:
                check_type('output_file_processor', 'dict')
                for output_file, pstring in \
                        data['output_file_processor'].items():
                    if 'outputs' in data and \
                        output_file not in data['outputs']:
                        errors.append("%s: no output file named %s defined in"
                                " outputs for output file processor" \
                                % exp_id)
                    try:
                        plist = pstring.split()
                        module = plist[0]
                        function = plist[1]
                    except:
                        errors.append("%s: couldn't get module or function"
                                    " from output file processor arguments" \
                                    % exp_id)
                    if not neronet.core.can_import(module, function):
                        errors.append("%s: can't import %s from %s" 
                                        " for output file processor" \
                                        % (exp_id, module, function))
                    
            if 'plot' in data:
                check_type('plot', 'dict')
                for plot_name, pstring in data['plot'].items():
                    try:
                        plist = pstring.split()
                        module = plist[0]
                        function = plist[1]
                        output_file = plist[2]
                        processor_found = False
                        if 'output_line_processor' in data:
                            if output_file in data['output_line_processor']:
                                processor_found = True
                        if not processor_found and \
                            'output_file_processor' in data:
                            if output_file in data['output_file_processor']:
                                processor_found = True
                        if not processor_found:
                            errors.append("%s: no output file named %s "
                                            "specified in outputs for plot" \
                                            % (exp_id, output_file))
                        if not neronet.core.can_import(module, function):
                            errors.append("%s: can't import %s from %s"
                                            " for plot" \
                                            % (exp_id, module, function))
                    except:
                        errors.append("%s: couldn't get module, function or"
                                        " output file from plot arguments" \
                                        % exp_id)
            if 'collection' in data:
                check_type('collection', 'list')
            if 'required_files' in data:
                if check_type('required_files', 'list'):
                    for required_file in data['required_files']:
                        filepath = os.path.join(folder, required_file)
                    
                        #Check that the main code file exists
                        #TODO: Maybe allow files not in the experiment folder?
                        if not os.path.exists(filepath):
                            errors.append("%s: no file named %s in "
                                            "folder %s" \
                                        % (exp_id, required_file, folder))
            if 'conditions' in data:
                for condition in data['conditions']:
                    cond_errors = self.check_condition(condition)
                    for error in cond_errors:
                        errors.append(exp_id + ": " + error)
            #TODO: Ask Samuel
            if 'sbatch_args' in data:
                pass
            if 'custom_msg' in data:
                check_type('custom_msg', 'string')

        def _process_data(scope):
            #Find experiment ids
            potential_exp_ids = set(scope) - definable_fields
            experiment_ids = set()
            for exp in potential_exp_ids:
                if exp[0] != '+':
                    errors.append("Invalid field '%s'" % exp)
                else:
                    experiment_ids.add(exp)
            
            #Find already defined fields
            defined_fields = set(scope) - potential_exp_ids

            for experiment_id in experiment_ids:
                experiment_scope = scope[experiment_id]
                
                #Turn empty experiment scope from None to a dict
                if not experiment_scope:
                    experiment_scope = {}
                               
                #Populate experiment scope with scope
                for field in defined_fields:
                    if field not in experiment_scope:
                        experiment_scope[field] = scope[field]
                    if field == 'parameters':
                        parameters = scope['parameters']
                        if field in experiment_scope:
                            for name, value in \
                                    experiment_scope['parameters'].items():
                                parameters[name] = value
                        experiment_scope['parameters'] = parameters
                
                #Create experiment data dict
                experiment_data = {field: value for field, value in \
                                    experiment_scope.items() \
                                    if field in definable_fields}
                experiment_data['experiment_id'] = experiment_id

                #Check that the user has defined the experiment data correctly
                _check_experiment_data(experiment_data)
                
                #Create the experiments if there hasn't been any errors
                if not errors:
                    params = []
                    if 'parameters' in experiment_data:
                        params = self._param_combinations( \
                                    experiment_data['parameters'])
                    if 'conditions' in experiment_data:
                        conditions = {}
                        for condition_name in experiment_data[field]:
                            condition = experiment_data['conditions'][condition_name]
                            condition['name'] = condition_name
                            condition['killvalue'] = float(condition['killvalue'])
                            conditions[condition_name] = \
                                    neronet.experiment.ExperimentWarning(**condition)
                            experiment_data['conditions'] = conditions

                    experiment_data['path'] = os.path.abspath(folder)
                    for param in params:
                        experiment_data['parameters'] = param
                        experiment_id = experiment_id[1:]
                        if len(params) > 1:
                            keys = sorted(param)
                            param_strings = [key + '-' + \
                                            str(param[key]) for key in keys]
                            name = '_'.join([experiment_id] + param_strings)
                            experiment_data['experiment_id'] = name
                        else:
                            experiment_data['experiment_id'] = experiment_id
                        experiments.append( \
                            neronet.experiment.Experiment(**experiment_data))
                _process_data(experiment_scope) 
        _process_data(data)
 
        if errors:
            raise FormatError(errors)
        if experiments:
            return experiments
        else:
            raise FormatError(['no experiments defined in config file'])

    def check_conditions(self, conditions):
        err = []
        for field in neronet.experiment.ExperimentWarning.WARNING_FIELDS:
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
