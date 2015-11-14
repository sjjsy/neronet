# neroman.py

import sys
import os

from core import Logger

# Parse arguments
experiment = ' '.join(sys.argv[1:])
# Define a logger
logger = Logger('MAN')
logger.log('Experiment: %s' % (experiment))
# Launch Mum on localhost (on ttft the SSH port is abnormal)
logger.log('Launching Mum!')
os.system('ssh -p 55565 localhost "cd %s; python3.5 neromum.py %s"'
    % (os.getcwd(), experiment))
logger.log('Mum finished!')