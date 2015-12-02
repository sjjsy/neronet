# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys

import neroman

def create_config_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    parser.add_argument('--experiment',
            metavar='folder',
            nargs=1,
            help='Creates experiments according to the config file found in'
            'the folder')
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
            help='Runs neroman')
    parser.add_argument('--status',
            nargs='?',
            const='all',
            help='Displays neronet status information')
    return parser

def main():
    """Parses the command line arguments and starts Neroman
    """
    parser = create_config_parser()
    args = parser.parse_args()
    nero = neroman.Neroman()
    if args.experiment:
        experiment_folder = args.experiment[0]
        try:
            nero.specify_experiments(experiment_folder)
            nero.save_database()
        except (FileNotFoundError, neroman.FormatError) as e:
            print(e)
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
            nero.status(args.status)
        except IOError as e:
            print(e)
    if args.submit:
        experiment_folder = args.submit[0]
        experiment_destination = args.submit[1]
        experiment = args.submit[2]
        cluster_address = args.submit[3]
        cluster_port = args.submit[4]
        nero.submit(experiment_folder)


if __name__ == '__main__':
    main()
