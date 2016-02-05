# -*- coding: utf-8 -*-
"""This module defines a test daemon for development purposes."""

import neronet.daemon

class Testdmn(neronet.daemon.Daemon):

    """A class to test the Daemon class."""

    def __init__(self):
        super(Testdmn, self).__init__('testdmn')

def main():
    """Create a CLI interface object and process CLI arguments."""
    cli = neronet.daemon.Cli(Testdmn())
    cli.parse_arguments()

if __name__ == '__main__':
    main()