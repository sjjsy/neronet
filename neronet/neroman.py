# -*- coding: utf-8 -*-
"""This module defines Neroman.

To work with Neroman each experiment must have the following attributes
defined in its config:

* experiment_id: The unique identifier for the experiment
* run_command_prefix: The run command of the experiment
* main_code_file: The code file to be run
* destination_folder: Folder that the experiment is run in on the cluster.
* parameters: The definition of the experiment parameters
* parameters_format: The format of the experiment parameters
* logoutput: The location the experiment outputs its output
* state: A tuple of the experiment state which is set to 'defined' by this
  function and the time changed
* cluster: The cluster that the experiment is running on. Set to
  None by this function
* time_created: Sets the current time as the creation time
* time_modified: The time the experiment was last modified. Sets
  this time to the same as the time created
* path: The absolute path to the folder

"""

import os
import time
import datetime
import os.path
import collections

import neronet.core
import neronet.config_parser

DATABASE_FILENAME = 'default.yaml'
PREFERENCES_FILENAME = 'preferences.yaml'
CLUSTERS_FILENAME = 'clusters.yaml'

class Neroman:

    """The part of Neronet that handles user side things.

    Attributes:
        clusters (Dict): A dictionary containing the specified clusters
        database (Dict): A dictionary containing the specified experiments
        preferences (Dict): A dictionary containing the preferences
    """

    def __init__(self):
        """Initializes Neroman

        Reads the contents of its attributes from yaml files or creates them
        """
        self.config_parser = neronet.config_parser.ConfigParser()
        self.clusters, self.preferences, self.database = \
            self.config_parser.load_configurations(CLUSTERS_FILENAME, \
                            PREFERENCES_FILENAME, DATABASE_FILENAME)

    def clean(self):
        """Removes all neronet related data"""
        self.config_parser.remove_data()

    def specify_cluster(
            self,
            cluster_name,
            ssh_address,
            cluster_type,
            portnumber=22):
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
            raise neronet.config_parser.FormatError( \
                        "Cluster type should be slurm or unmanaged")

        self.clusters['clusters'][cluster_name] = {'ssh_address': ssh_address,
                                                   'type': cluster_type,
                                                   'port': portnumber}

        self.config_parser.save_clusters(CLUSTERS_FILENAME, self.clusters)

    def specify_experiments(self, folder):
        """Specify experiments so that Neroman is aware of them.

        Reads the contents of the experiment from a config file inside the
        specified folder.

        Args:
            folder (str): The path of the folder that includes
                the experiment that's being specified.

        Raises:
            IOError: If the folder doesn't exists or the config file
                doesn't exists
            FormatError: If the config file is badly formated
        """


        experiments = self.config_parser.parse_experiments(folder)
        for experiment in experiments:
            if experiment.id in self.database:
                raise IOError("Experiment named %s already in the database" \
                                % experiment.id)
            else: self.database[experiment.id] = experiment
        self.config_parser.save_database(DATABASE_FILENAME, \
                                        self.database)

    def specify_user(self, name, email, default_cluster = ""):
        """Update user data"""
        self.preferences['name'] = name
        self.preferences['email'] = email
        self.preferences['default_cluster'] = default_cluster
        self.config_parser.save_preferences(PREFERENCES_FILENAME, \
                                            self.preferences)

    def delete_experiment(self, experiment_id):
        """Deletes the experiment with the given experiment id

        Parameters:
            experiment_id (str): id of the experiment to be deleted
        Raises:
            KeyError: if the experiment with the given id doesn't exist
        """
        self.database.pop(experiment_id)
        self.config_parser.save_database(DATABASE_FILENAME, \
                                        self.database)

    def get_experiment_results(self, experiment_id, remote_dir, local_dir):
        """Get the experiment results from neromum

        Args:
            experiment_id (str): the experiment ID.
            remote_dir (str): the file path to results folder on the remote
                machine.
            local_dir (str): the file path to results folder on the local
                machine.
        """
        experiment = self.database[experiment_id]
        cluster_ID = experiment.cluster
        cluster_port = self.clusters['clusters'][cluster_ID]['port']
        cluster_address = self.clusters['clusters'][cluster_ID]['ssh_address']
        neronet.core.osrun(
            'rsync -az -e "ssh -p%s" "%s:%s" "%s"'
            % (cluster_port, cluster_address,
                remote_dir, local_dir))

    def status_gen(self, arg):
        """Creates a generator that generates the polled status

        Yields:
            str: A line of neroman status
        """
        if arg != 'all':
            if arg in self.database:
                experiment = self.database[arg]
                for line in experiment.as_gen():
                    yield line
                raise StopIteration
            else:
                raise IOError('No experiment named %s' % arg)
        yield "================Neroman=================\n"
        yield "\n"
        yield "================User====================\n"
        yield "Name: %s\n" % self.preferences['name']
        yield "Email: %s\n" % self.preferences['email']
        if self.preferences['default_cluster']:
            yield "Default Cluster: %s\n" % self.preferences['default_cluster']
        yield "\n"
        yield "================Clusters================\n"
        if not self.clusters['clusters']:
            yield "No clusters defined\n"
        else:
            clusters = self.clusters['clusters']
            for cluster in clusters:
                cluster_name = cluster
                cluster = clusters[cluster]
                address = cluster['ssh_address']
                type = cluster['type']
                yield "%s:\n" % cluster_name
                yield "  Address: %s\n" % address
                yield "  Type: %s\n" % type 
                for key, value in cluster.iteritems():
                    if key != 'ssh_address' and key != 'type':
                        yield "  %s: %s\n" % (key.capitalize(), value)
        yield "\n"
        yield "================Experiments=============\n"
        if not len(self.database):
            yield "No experiments defined\n"
        else:
            experiments_by_state = self._partition_by_state(self.database)
            current = ""
            for state, experiments in sorted(experiments_by_state.iteritems()):
                yield "%s:\n" % state.capitalize()
                for experiment in sorted(experiments, key=lambda e: e.id):
                    yield "  %s\n" % experiment.id

    def _partition_by_state(self, experiments):
        """Partitions the experiments in the database by state"""
        experiments_by_state = collections.defaultdict(list)
        for experiment in experiments.values():
            experiments_by_state[experiment.state[-1][0]].append(experiment)
        return experiments_by_state

    def send_files(
        self,
        experiment_folder,
        remote_dir,
        cluster_address,
        cluster_port,
        neronet_root=os.getcwd(),
    ):
        """Send experiment files to the cluster

        Args:
            experiment_folder (str): the file path to experiment folder on the local machine.
            remote_dir (str): the file path to experiment folder on the remote cluster.
            neronet_root (str): the file path to neronet folder.
            cluster_address (str): the address of the cluster.
            cluster_port (int): ssh port number of the cluster.
        """
        tmp_dir = '/tmp/neronet-tmp'
        # rsync the neronet files to tmp
        neronet.core.osrun(
            'rsync -az "%s" "%s"' %
            (neronet_root +
             '/neronet',
             tmp_dir))
        # rsync bin files to tmp
        neronet.core.osrun(
            'rsync -az "%s" "%s"' %
            (neronet_root + '/bin', tmp_dir))
        # rsync the experiment files to tmp
        neronet.core.osrun(
            'rsync -az "%s/" "%s"' %
            (experiment_folder, tmp_dir))
        neronet.core.osrun(
            'rsync -az -e "ssh -p%s" "%s/" "%s:%s"' %
            (cluster_port,
             tmp_dir,
             cluster_address,
             remote_dir))

    def submit(self, exp_id, cluster_ID = ""):
        """Main loop of neroman.

        Start the experiment in the cluster using ssh.

        Args:
            experiment_folder (str) : the file path to experiment folder in local machine.
            experiment_destination (str) : the file path to experiment folder on the remote cluster.
            experiment (str) : the name of the experiment.
            cluster_address (str) : the address of the cluster.
            cluster_port (int) : ssh port number of the cluster.
        """
        if not cluster_ID:
            cluster_ID = self.preferences['default_cluster']
            
        if cluster_ID not in self.clusters['clusters']:
            raise IOError('The given cluster ID or default cluster is not valid')
        
        remote_dir = '/tmp/neronet-%d' % (time.time())
        experiment_destination = self.database[exp_id].path + \
            "/" + self.database[exp_id].logoutput
        experiment_folder = self.database[exp_id].path
        #experiment = self.database[exp_id]["path"]+"/"+self.database[exp_id]["main_code_file"]
        experiment_parameters = self.database[exp_id].callstring
        cluster_port = self.clusters['clusters'][cluster_ID]["port"]
        cluster_address = self.clusters["clusters"][cluster_ID]["ssh_address"]
        self.send_files(
            experiment_folder,
            remote_dir,
            cluster_address,
            cluster_port)
        # Magic do NOT touch:
        neronet.core.osrun(
            'ssh -p%s %s "cd %s; PATH="%s/bin:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="%s" neromum %s"' %
            (cluster_port,
             cluster_address,
             remote_dir,
             remote_dir,
             remote_dir,
             experiment_parameters))
        self.database[exp_id].cluster = cluster_ID
        self.update_state(exp_id, 'submitted')
        self.config_parser.save_database(DATABASE_FILENAME, \
                                        self.database)
        time.sleep(2)  # will be unnecessary as soon as daemon works
        # returns the results, should be called from cli
        self.get_experiment_results(exp_id, remote_dir, experiment_destination)
