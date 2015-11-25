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
    args = parser.parse_args()
    nero = neroman.Neroman()
    if args.experiment:
        experiment_folder = args.experiment[0]
        nero.specify_experiments(experiment_folder)
        nero.save_database()

if __name__ == '__main__':
    main()
