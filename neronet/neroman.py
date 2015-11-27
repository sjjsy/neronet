# -*- coding: utf-8 -*-
"""The module that starts up Neroman

This module implements the Command Line Interface of Neroman.

Attributes:
    CONFIG_FILENAME (str): The name of the config file inside the
        experiment folder that specifies the experiment.
"""

import os

import yaml


CONFIG_FILENAME = 'config.yaml'

class Neroman():
    """The part of Neronet that handles user side things.

    Attributes:
        database (str): Path to the database used, currently only .yaml
        clusters (Dict): A dictionary containing the specified clusters
        experiments (Dict): A dictionary containing the specified experiments
        preferences (Dict): A dictionary containing the preferences
    """

    def __init__(self, database = 'default.yaml', 
                        preferences_file = 'preferences.yaml', 
                        clusters_file = 'clusters.yaml'):
        """Initializes Neroman

        Reads the contents of its attributes from a database (currently just
        a .yaml file).
        
        Args:
            database (str): The path to the database file as a string, the
                rest of the attributes will be parsed from the database.
        """
        self.database = database
        self.clusters_file = clusters_file
        self.preferences_file = preferences_file
        self.clusters = {}
        self.experiments = {}
        self.preferences = {}
        self._load_configurations(database, clusters_file, preferences_file)

    def _load_configurations(self, database, clusters, preferences):
        """Load the configurations from the yaml files or creates them if they
        don't exist
        
        Args:
            database (str): The filepath of the database file
            clusters (str): The filepath of the clusters file
            preferences (str): The filepath of the preferences file
        """
        if not os.path.exists(preferences):
            with open(preferences, 'w') as f:
                f.write("name:\nemail:\n")
        else:
            with open(preferences, 'r') as f:
                self.preferences = yaml.load(f.read())
        if not self.preferences: self.preferences = {}

        if not os.path.exists(clusters):
            with open(clusters, 'w') as f:
                f.write("clusters:\ngroups:\n")
        else:
            with open(clusters, 'r') as f:
                self.clusters = yaml.load(f.read())
        if not self.clusters: self.clusters = {'clusters': None }
        if not self.clusters['clusters']: self.clusters['clusters'] = {}
        
        if not os.path.exists(database):
            with open(database, 'w') as f:
                f.write('')
        else:
            with open(database, 'r') as f:
                self.experiments = yaml.load(f.read())
        if not self.experiments: self.experiments = {}
    
    def save_database(self):
        """Save the contents of Neroman's attributes in the database
        """
        with open(self.database, 'w') as f:
            f.write(yaml.dump(self.experiments,
                default_flow_style=False))

    def specify_cluster(self, cluster_name, ssh_address, cluster_type):
        """Specify clusters so that Neroman is aware of them.
        
        Writes cluster name, address and type to the clusters config file
    
        Args:
            cluster_name (str): The name of the cluster, should be unique
            ssh_address (str): SSH address of the cluster
            cluster_type (str): Type of the cluster. Either slurm or unmanaged

        Raises:
            FormatError: if the cluster type isn't unmanaged or slurm

        """
        if cluster_type != 'slurm' and cluster_type != 'unmanaged':
            raise FormatError("Cluster type should be slurm or unmanaged")

        print(self.clusters)
        self.clusters['clusters'][cluster_name] = {'ssh_address': ssh_address, 
                                                    'type': cluster_type}
        with open(self.clusters_file, 'w') as f:
            f.write(yaml.dump(self.clusters, default_flow_style=False))

    def specify_experiments(self, folder):
        """Specify experiments so that Neroman is aware of them.

        Reads the contents of the experiment from a config file inside the
        specified folder. 

        Args:
            folder (str): The path of the folder that includes 
                the experiment that's being specified.

        Raises:
            FileNotFoundError: If the folder doesn't exists or the config file
                doesn't exists
            FormatError: If the config file is badly formated
        """
        if not os.path.isdir(folder):
            raise FileNotFoundError('No such folder')
        
        file_path = os.path.join(folder, CONFIG_FILENAME)
        if not os.path.exists(file_path):
            raise FileNotFoundError('No config file in folder')

        if os.stat(file_path).st_size == 0:
            raise FormatError('Empty config file')

        with open(file_path, 'r') as file:
            experiment_data = yaml.load(file.read())
        experiment = {}
        for field in ['run_command_prefix', 'main_code_file',
                        'parameters', 'parameters_format']:
            if field not in experiment_data:
                raise FormatError('No %s field in experiment' % field)
            experiment[field] = experiment_data[field]
        experiment['status'] = 'defined'
        self.experiments[folder] = experiment
        self.save_database()

    def specify_user(self, name, email):
        """ Updates user data
        """
        self.preferences['name'] = name
        self.preferences['email'] = email
        with open(self.preferences_file, 'w') as f:
            f.write(yaml.dump(self.preferences, default_flow_style=False))

        

    def status(self):
        """ Displays Neroman data on into stdstream
        """
        print("Neroman")
        print("Clusters")
        if not self.clusters['clusters']:
            print("No clusters defined")
        else:
             for cluster in self.clusters['clusters']:
                address = self.clusters['clusters'][cluster]['ssh_address']
                type = self.clusters['clusters'][cluster]['type']
                print("{} {} {}".format(cluster, address, type))
        print('No' if not len(self.experiments) else len(self.experiments), 
                "experiments defined")

class FormatError(Exception):
    """ Exception raised when experiment config file is poorly formatted
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

