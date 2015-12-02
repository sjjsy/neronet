# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys

import neroman

def create_parser():
    parser = ArgumentParser()
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
    parser.add_argument('--status',
            action='store_true',
            help='Displays neronet status information')
    parser.add_argument('--run',
            nargs=1,
            help='Runs neroman')
    return parser
            
def main():
    """Parses the command line arguments and starts Neroman
    """
    parser = create_parser()
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
    if args.run:
        neroman.run()    

if __name__ == '__main__':
    main()

