# -*- coding: utf-8 -*-
import os
from pathlib import Path
from argparse import ArgumentParser
import time
import os
import yaml

CONFIG_FILENAME = 'config.yaml'


"""The module that starts up Neroman

This module implements the Command Line Interface of Neroman.

Attributes:
    CONFIG_FILENAME (str): The name of the config file inside the
        experiment folder that specifies the experiment.
"""
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
        experiment['path'] = folder
        if 'experiment_id' not in experiment_data:
            raise FormatError('No experiment_id field in experiment')
        else:
            self.experiments[experiment_data['experiment_id']] = experiment
        self.save_database()

    def specify_user(self, name, email):
        """ Updates user data
        """
        self.preferences['name'] = name
        self.preferences['email'] = email
        with open(self.preferences_file, 'w') as f:
            f.write(yaml.dump(self.preferences, default_flow_style=False))

    def get_experiment_results(self, remote_results = Path('/tmp/default'), local_results = Path('/home/tukez/neronet/test/results'), cluster_address='localhost', cluster_port=22):
        """Get the experiment results from neromum

        Args:
            remote_results (str) : the file path to results folder on the remote cluster.
            local_results (str) : the file path to results folder on the local machine.
            cluster_address (str) : the address of the cluster.
            cluster_port (int) : ssh port number of the cluster.
        """
        os.system(
            'rsync -avz -e "ssh -p%s" "%s:%s" "%s"'
            % (cluster_port, cluster_address,
                remote_results, local_results))


    def status(self):
        """ Displays Neroman data on into stdstream
        """
        print("================Neroman=================")
        print("\n================Clusters================")
        if not self.clusters['clusters']:
            print("No clusters defined")
        else:
             for cluster in self.clusters['clusters']:
                address = self.clusters['clusters'][cluster]['ssh_address']
                type = self.clusters['clusters'][cluster]['type']
                print("{} {} {}".format(cluster, address, type))
        print("\n================Experiments=============")
        if not len(self.experiments):
            print("No experiments defined")
        else:
            for experiment in self.experiments:
                print(experiment + ': ' + self.experiments[experiment]['status'])

    def send_files(self, experiment_folder, experiment_destination='/tmp/default', neronet_root=Path(os.getcwd()), cluster_address='localhost', cluster_port='22'):
        """Send experiment files to the cluster

        Args:
            experiment_folder (str) : the file path to experiment folder on the local machine.
            experiment_destination (str) : the file path to experiment folder on the remote cluster.
            neronet_root (str) : the file path to neronet folder.
            cluster_address (str) : the address of the cluster.
            cluster_port (int) : ssh port number of the cluster.
        """

        tmp_dir = Path('/tmp/neronet-tmp')
        #os.system('rsync -az --delete "%s/" "%s"' % (experiment_folder, tmp_dir)) #clear the tmp folder
        os.system('rsync -avz          "%s" "%s"' % (neronet_root / 'neronet', tmp_dir)) #rsync the neronet files to tmp
        os.system('rsync -avz          "%s" "%s"' % (neronet_root / 'bin', tmp_dir)) #rsync bin files to tmp
        os.system('rsync -avz --delete -e "ssh -p%s" "%s/" "%s:%s"'
            % (cluster_port, tmp_dir, cluster_address, experiment_destination))
        #os.system('rm -r "%s"' % (tmp_dir)) # remove the tmp folder as it is no longer needed

    def run(self, experiment_destination="/tmp/default/", cluster_address="localhost", cluster_port=22, experiment="/tmp/default/neronet/sleep.py"):
        """Main loop of neroman

        Start the experiment in the cluster using ssh

        Args:
            experiment_destination (str) : the file path to experiment folder on the remote cluster.
            cluster_address (str) : the address of the cluster.
            cluster_port (int) : ssh port number of the cluster.
            experiment (str) : the name of the experiment.
        """

        os.system('ssh -p%s %s "cd %s; PATH="%s/bin:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="%s" neromum %s 10 0.5"' #magic do NOT touch
                  % (cluster_port, cluster_address, experiment_destination, experiment_destination, experiment_destination, experiment))
        time.sleep(10) #will be unnecessary as soon as daemon works
        self.get_experiment_results() #returns the results, should be called from cli


class FormatError(Exception):
    """ Exception raised when experiment config file is poorly formatted
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
