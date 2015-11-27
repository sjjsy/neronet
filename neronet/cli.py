# -*- coding: utf-8 -*-

from argparse import ArgumentParser

import neroman

def main():
    """Parses the command line arguments and starts Neroman
    """
    parser = ArgumentParser()
    parser.add_argument('--experiment',
            metavar='folder',
            nargs=1)
    parser.add_argument('--cluster',
            metavar=('id', 'address', 'type'),
            nargs=3)
    parser.add_argument('--user',
            metavar=('name', 'email'),
            nargs=2)
    parser.add_argument('--status',
            nargs='?',
            default='all', status_parser = parser.add_subparsers())
    args = parser.parse_args()
    nero = neroman.Neroman()
    if args.experiment:
        experiment_folder = args.experiment[0]
        nero.specify_experiments(experiment_folder)
        nero.save_database()
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
        nero.status()

if __name__ == '__main__':
    main()
