# neroman.py
#
# one line description

import yaml
import csv

class Neroman():
    def __init__(self,config_file='default.cfg'):
        """Neroman init method
        Args:
            config_file (string): Filename of the configuration file
        """
        self.clusters = {}
        self.experiments = []
        parse_configurations(config_file)

    def load_configurations(filename='default.cfg'):
        """Parse the config file given by researcher."""
        with open(filename, 'r') as file:
            configs = yaml.load(file.read())
        self.clusters = configs['clusters']
        #self.experiments configs['experiments'] #maybe?

    def add_cluster(name, address):
        """Adds a cluster to self.clusters"""
        self.clusters[name] = {'address': address}

    def create_experiment(experiment_filename, data_filename):
        """Creates an experiment

        Args:
            experiment_filename (string): Filename of the experiment file
            data_filename (string): Filename of the data file
        Return:
            experiment (nerokid): Created experiment nerokid
        """
        self.experiments.append((experiment_filename, data_filename))
        #with open(data_filename, 'r') as file:
        #    reader = csv.reader(file)
        #pass

    def install_neromum():
        """Creates a Neromum and installs it to destination."""
        os.system('ssh ' + ssh_params)
        pass

    def get_available_clusters():
        """Returns the info on available clusters in the given network."""
        pass
    
    def get_experiments():
        """Returns the past experiments"""
        pass
    
    def display_experiments():
        """Displays experiments to user"""
        pass

def main():
    """The Neroman main."""
    pass 

if __name__ == '__main__':
    main()