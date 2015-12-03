# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys

import neronet.neroman


def create_config_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '--experiment',
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
                        help='Submits an experiment to be run')
    parser.add_argument('--status',
                        metavar='experiment_id',
                        nargs='?',
                        const='all',
                        help='Displays neronet status information')
    return parser


def main():
    """Parses the command line arguments and starts Neroman
    """
    parser = create_config_parser()
    args = parser.parse_args()
    nero = neronet.neroman.Neroman()
    if args.experiment:
        experiment_folder = args.experiment[0]
        try:
            nero.specify_experiments(experiment_folder)
            nero.save_database()
        except (FileNotFoundError, neronet.neroman.FormatError) as e:
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
        cluster_ID = args.submit[1]
        nero.submit(experiment_folder, cluster_ID)


if __name__ == '__main__':
    main()
