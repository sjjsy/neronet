# neroman.py
#
# one line description

import yaml
import argparse
import csv


class Neroman():
    def __init__(self,config_file='default.cfg'):
        """Neroman init method
        Args:
            config_file (string): Filename of the configuration file
        """
        self.clusters = {}
        self.experiments = []
        self.load_configurations(config_file)

    def load_configurations(self, filename='default.cfg'):
        """Parse the config file given by researcher."""
        with open(filename, 'r') as file:
            configs = yaml.load(file.read())
        self.clusters = configs['clusters']
        #self.experiments configs['experiments'] #maybe?

    def add_cluster(self, name, address, scheduler_type):
        """Adds a cluster to self.clusters"""
        self.clusters[name] = {'address': address, 'type': scheduler_type}

    def add_experiment(self, experiment_folder):
        """Creates an experiment

        Args:
            experiment_filename (string): Filename of the experiment file
            data_filename (string): Filename of the data file
        Return:
            experiment (nerokid): Created experiment nerokid
        """
        pass

    def install_neromum(self):
        """Creates a Neromum and installs it to destination."""
        pass

    def get_available_clusters(self):
        """Returns the info on available clusters in the given network."""
        print(self.clusters)
           
            
    
    def get_experiments(self):
        """Returns the past experiments"""
        pass
    
    def display_experiments(self):
        """Displays experiments to user"""
        pass

    def submit_experiment(self, cluster_name, experiment_name):
        pass

    def monitor_experiment(self, experiment_name):
        pass

def main():
    """The Neroman main."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster', 
            metavar=('cluster_name', 'cluster_address', 'scheduler_type'), 
            nargs=3)
    parser.add_argument('--experiment',
            metavar='experiment_folder',
            nargs=1)
    parser.add_argument('--submit',
            metavar=('cluster_name', 'experiment_name'),
            nargs=2)
    parser.add_argument('--monitor',
            metavar='experiment_name',
            nargs=1)
    args = parser.parse_args()
    
    neroman = Neroman()
    if args.cluster:
        cluster_name = args.cluster[0]
        cluster_address = args.cluster[1]
        scheduler_type = args.cluster[2]
        neroman.add_cluster(cluster_name, cluster_address, scheduler_type)
    if args.experiment:
        experiment_folder = args.experiment[0]
        neroman.add_experiment(experiment_folder)
    if args.submit:
        cluster_name = args.submit[0]
        experiment_name = args.submit[1]
        neroman.submit_experiment(cluster_name, experiment)
    if args.monitor:
        experiment_name = args.monitor[0]
        neroman.monitor_experiment(experiment_name)
    neroman.get_available_clusters()

if __name__ == '__main__':
    main()
