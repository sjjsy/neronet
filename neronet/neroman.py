import os.path
from argparse import ArgumentParser

import yaml

CONFIG_FILENAME = 'config.yaml'


class Neroman():
    """
    """

    def __init__(self, database = "default.yaml"):
        """
        """
        self.database = database
        self.clusters = {}
        self.experiments = {}
        self.preferences = {}
        self._load_database(database)

    def _load_database(self, filename):
        """Load the database from an yaml file"""
        with open(filename, 'r') as file:
            database = yaml.load(file.read())
        self.clusters = database.get('clusters', {})
        self.experiments = database.get('experiments', {})
        self.preferences = database.get('preferences', {})
    
    def specify_experiment(self, folder):
        """
        """
        with open(os.path.join(folder, CONFIG_FILENAME), 'r') as file:
            experiment_data = yaml.load(file.read())
        try:
            experiment = {}
            for field in ['run_command_prefix', 'main_code_file',
                        'parameters', 'parameters_format']:
                experiment[field] = experiment_data[field]
            self.experiments[folder] = experiment
        except KeyError:
            print("Error while loading experiment")


def main():
    """
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


if __name__ == '__main__':
    main()
