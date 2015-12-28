# -*- coding: utf-8 -*-
import datetime
import os

import yaml


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
        return '\n'.join(self.value)

class ConfigParser():
    def _time_now(self):
        return datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')

    def parse_experiment(self, folder, config_file):
        
        with open(config_file, 'r') as file:
            data = yaml.load(file.read())
        
        
        errors = []
        experiments = {}
        scp = {}
            
        def __read_experiments(d, scope, scope_no, e):
            fields = ['run_command_prefix', 'main_code_file',
                'parameters', 'parameters_format', 'logoutput',
                'collection']
            #Populate the scope
            for field in fields:
                if field in d:
                    old_scope = scope.get(field, [])
                    old_scope.append((scope_no, d[field]))
                    scope[field] = old_scope
            #Find the experiment ids
            experiment_ids = set(d) - set(fields)
            for experiment_id in experiment_ids:
                __read_experiments(d[experiment_id], scope, scope_no + 1, e)
                experiment = {}
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
                    
        __read_experiments(data, scp, 0, errors)
        if errors:
            raise FormatError(errors)
        return experiments
