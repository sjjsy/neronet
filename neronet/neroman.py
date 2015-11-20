# -*- coding: utf-8 -*-
"""The module that starts up Neroman

This module implements the Command Line Interface of Neroman.

Attributes:
    CONFIG_FILENAME (str): The name of the config file inside the
        experiment folder that specifies the experiment.
"""

import os
from argparse import ArgumentParser

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

    def __init__(self, database = "default.yaml"):
        """Initializes Neroman

        Reads the contents of its attributes from a database (currently just
        a .yaml file).
        
        Args:
            database (str): The path to the database file as a string, the
                rest of the attributes will be parsed from the database.
        """
        self.database = database
        self.clusters = {}
        self.experiments = {}
        self.preferences = {}
        self._load_database(database)

    def _load_database(self, filename):
        """Load the database from an yaml file
        
        Args:
            filename (str): The filepath of the database file
        """
        if os.stat(filename).st_size == 0:
            return
        with open(filename, 'r') as file:
            database = yaml.load(file.read())
        self.clusters = database.get('clusters', {})
        self.experiments = database.get('experiments', {})
        self.preferences = database.get('preferences', {})
    
    def save_database(self):
        """Save the contents of Neroman's attributes in the database
        """
        with open(self.database, 'w') as file:
            file.write(yaml.dump({'preferences': self.preferences}, 
                default_flow_style=False))
            file.write(yaml.dump({'clusters': self.clusters}, 
                default_flow_style=False))
            file.write(yaml.dump({'experiments': self.experiments},
                default_flow_style=False))


    def specify_experiment(self, folder):
        """Specify experiments so that Neroman is aware of them.

        Reads the contents of the experiment from a config file inside the
        specified folder. 

        Args:
            folder (str): The path of the folder that includes 
                the experiment that's being specified.
        Returns:
            True or False: If it fails then it raises an error or
                returns False.
        """
        file_path = os.path.join(folder, CONFIG_FILENAME)
        if os.stat(file_path).st_size == 0:
            print("Empty config file")
            return False

        with open(file_path, 'r') as file:
            experiment_data = yaml.load(file.read())
        try:
            experiment = {}
            for field in ['run_command_prefix', 'main_code_file',
                        'parameters', 'parameters_format']:
                experiment[field] = experiment_data[field]
            self.experiments[folder] = experiment
        except KeyError:
            print("Error while loading experiment")
            return False
        return True


def main():
    """Parses the command line arguments and starts Neroman
    """
    parser = ArgumentParser()
    parser.add_argument('--experiment',
            metavar='folder',
            nargs=1)
    args = parser.parse_args()
    neroman = Neroman()
    if args.experiment:
        experiment_folder = args.experiment[0]
        neroman.specify_experiment(experiment_folder)
        neroman.save_database()

if __name__ == '__main__':
    main()
