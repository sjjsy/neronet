# main.py
#
# Usage: main.py IN_FILE OUT_FILE
# Examples:
#   main.py in.txt out.txt
#
# Computes the sum of the numbers in IN_FILE and writes it into OUT_FILE.

import sys
import time
import datetime

# Define a log function
def log(msg):
  sys.stdout.write('%s: %s\n' % (datetime.datetime.now(), msg))
  sys.stdout.flush()

# Load IO files
pfi = sys.argv[1]
pfo = sys.argv[2]

# Read the numbers
log('Reading the numbers...')
with open(pfi, 'r') as f:
  numbers = f.read().split(' ')
number_count = len(numbers)
time.sleep(number_count)

# Convert them to floats
for i in range(number_count):
  log('Loading %d/%d...' % (i+1, number_count))
  numbers[i] = float(numbers[i])
  time.sleep(numbers[i])

# Compute the sum
log('Computing the sum...')
the_sum = sum(numbers)
time.sleep(the_sum)

# Write it into the OUT_FILE
log('Writing the result...')
with open(pfo, 'w') as f:
  f.write(str(the_sum))
