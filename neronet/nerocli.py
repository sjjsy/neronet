# -*- coding: utf-8 -*-
"""This module implements the Command Line Interface of Neroman.
"""


import os.path
import argparse
import sys

import neronet.neroman

def create_argument_parser():
    """Create and return an argument parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment',
                        metavar='folder',
                        nargs=1,
                        help='Creates experiments according to the config'
                        'file found in the folder')
    parser.add_argument('--delete',
                        metavar='experiment id',
                        nargs=1,
                        help='Deletes the experiment with the given id')
    parser.add_argument('--cluster',
                        metavar=('id', 'address', 'type'),
                        nargs=3,
                        help='Specify a new cluster for computing')
    parser.add_argument('--user',
                        metavar=('name', 'email'),
                        nargs=2,
                        help='Updates user information')
    parser.add_argument('--submit',
                        nargs="+",
                        help='Submits an experiment to be run')
    parser.add_argument('--status',
                        metavar='experiment_id',
                        nargs='?',
                        const='all',
                        help='Displays neronet status information')
    parser.add_argument('--clean',
                        action='store_true',
                        help='Removes files created by neroman')
    return parser


def main():
    """Parses the command line arguments and starts Neroman."""
    parser = create_argument_parser()
    args = parser.parse_args()
    nero = neronet.neroman.Neroman()
    if args.experiment:
        experiment_folder = args.experiment[0]
        try:
            nero.specify_experiments(experiment_folder)
        except (IOError, neronet.config_parser.FormatError) as e:
            print e
    if args.delete:
        experiment_id = args.delete[0]
        try:
            nero.delete_experiment(experiment_id)
        except KeyError:
            print "No experiment named %s" % experiment_id
    if args.cluster:
        cluster_id = args.cluster[0]
        address = args.cluster[1]
        cluster_type = args.cluster[2]
        nero.specify_cluster(cluster_id, address, cluster_type)
    if args.user:
        name = args.user[0]
        email = args.user[1]
        nero.specify_user(name, email)
    if args.status:
        try:
            status_gen = nero.status_gen(args.status)
            print ''.join(status_gen),
        except IOError as e:
            print e
    if args.submit:
        experiment_ID = args.submit[0]
        if len(args.submit) > 1:
            cluster_ID = args.submit[1]
            nero.submit(experiment_ID, cluster_ID)
        else:
            nero.submit(experiment_ID)
    if args.clean:
        nero.clean()

def remove_dir(path):
    os.system('rm -r ' + path)
if __name__ == '__main__':
    main()
