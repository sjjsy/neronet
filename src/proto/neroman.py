# neroman.py

import os

from core import Logger

# Define a logger
logger = Logger('MAN')
# Launch Mum on localhost (on ttft the SSH port is abnormal)
logger.log('Launching Mum!')
os.system('ssh -p 55565 localhost "cd %s; python3.5 neromum.py python3.5 sleep.py 12 0.4"'
    % (os.getcwd()))
logger.log('Mum finished!')