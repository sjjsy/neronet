import os
from pathlib import Path
from argparse import ArgumentParser

#import yaml

CONFIG_FILENAME = 'config.yaml'


class Neroman():

    """
    """

    def __init__(self, database="default.yaml"):
        """
        """
        self.database = database
        self.clusters = {}
        self.experiments = {}
        self.preferences = {}
        self._load_database(database)

    def _load_database(self, filename):
        """Load the database from an yaml file"""
        if os.stat(filename).st_size == 0:
            return
        with open(filename, 'r') as file:
            database = yaml.load(file.read())
        self.clusters = database.get('clusters', {})
        self.experiments = database.get('experiments', {})
        self.preferences = database.get('preferences', {})

    def save_database(self):
        with open(self.database, 'w') as file:
            file.write(yaml.dump({'preferences': self.preferences},
                                 default_flow_style=False))
            file.write(yaml.dump({'clusters': self.clusters},
                                 default_flow_style=False))
            file.write(yaml.dump({'experiments': self.experiments},
                                 default_flow_style=False))

    def specify_experiment(self, folder):
        """
        """
        file_path = os.path.join(folder, CONFIG_FILENAME)
        if os.stat(file_path).st_size == 0:
            print("Empty config file")
            return

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

    def run(self):
        experiment = "sleep.py"
        experiment_source = Path.cwd()
        experiment_destination = Path('/tmp')  # get from experiment name
        cluster_address = 'localhost'
        cluster_port = 22
        os.system(
            'rsync -avz --progress -e "ssh -p%s" "%s" "%s:%s"'
            % (cluster_port, experiment_source, cluster_address,
                experiment_destination))
        os.system('ssh -p%s %s "cd %s/neronet; python3.5 neromum.py %s 10 0.5"'  # parse arguments
                  % (cluster_port, cluster_address, experiment_destination, experiment))


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
        neroman.save_database()
    neroman.run()