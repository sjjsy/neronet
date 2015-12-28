# -*- coding: utf-8 -*-
import datetime
import os

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
    def _time_now(self):
        return datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')

    def parse_experiments(self, folder):
        
        if not os.path.isdir(folder):
            raise FileNotFoundError('No such folder')

        config_file = os.path.join(folder, CONFIG_FILENAME)
        if not os.path.exists(config_file):
            raise FileNotFoundError('No config file in folder')

        if os.stat(config_file).st_size == 0:
            raise FormatError(['Empty config file'])
        
        with open(config_file, 'r') as file:
            data = yaml.load(file.read())
        
        
        errors = []
        experiments = {}


        def _read_experiments(old_scope):
            fields = ['run_command_prefix', 'main_code_file',
                'parameters', 'parameters_format', 'logoutput',
                'collection']
            
            #Get the experiment ids from the scope
            experiment_ids = set(old_scope) - set(fields)
            for experiment_id in experiment_ids:
                #Initialize the new scope with all under the experiment id
                new_scope = old_scope[experiment_id]
                
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
                
                experiment = {}
                if not errors:
                    for field in fields:
                        experiment[field] = new_scope[field]
                    experiment['cluster'] = None
                    experiment['time_created'] = self._time_now()
                    experiment['state'] = [['defined', experiment['time_created']]]
                    experiment['time_modified'] = experiment['time_created']
                    experiment['path'] = os.path.abspath(folder)
                    experiments[experiment_id] = experiment
                _read_experiments(new_scope)
        
        """ A worse iteration of parse code
        def __read_experiments(d, scope, scope_no):
            fields = ['run_command_prefix', 'main_code_file',
                'parameters', 'parameters_format', 'logoutput',
                'collection']
            #Populate the scope
            print("Depth:", scope_no, "data:", data)
            for field in fields:
                if field in d:
                    old_scope = scope.get(field, [])
                    old_scope.append((scope_no, d[field]))
                    scope[field] = old_scope
            #Find the experiment ids
            experiment_ids = set(d) - set(fields)
            for experiment_id in experiment_ids:
                __read_experiments(d[experiment_id], scope, scope_no + 1)
                experiment = {}
                print(experiment, scope)
                for field in fields:
                    if field in scope:
                        experiment[field] = scope[field][-1][1]
                        if scope[field][-1][0] > scope_no: scope[field].pop()
                    else: errors.append('No %s field in experiment %s' % \
                                        (field, experiment_id))
                if not errors:
                    experiment['cluster'] = None
                    experiment['time_created'] = self._time_now()
                    experiment['state'] = [['defined', experiment['time_created']]]
                    experiment['time_modified'] = experiment['time_created']
                    experiment['path'] = os.path.abspath(folder)
                    experiments[experiment_id] = experiment
        """            
        _read_experiments(data)

        if errors:
            raise FormatError(errors)
        return experiments
