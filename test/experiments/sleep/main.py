# main.py
#
# Usage: main.py count interval
# Examples:
#   main.py 4 10
#   main.py 100 0.4
#
# Writes the system time <count> times into stdout with an interval of
# <interval> seconds

import sys
import time
import datetime

count = int(sys.argv[1])
interval = float(sys.argv[2])

for i in range(1, count+1):
    time.sleep(interval)
    print('%d, %d, %d' % (i, i*i, i*i*i))
    sys.stdout.flush()
