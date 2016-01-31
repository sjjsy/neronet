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
import random

count = int(sys.argv[1])
interval = float(sys.argv[2])

for i in range(1, count+1):
    time.sleep(interval)
    print('%s: %d/%d (%.1f)' % (datetime.datetime.now(), i, count, interval))
    print('test ' + str(random.random()*100))
    sys.stdout.flush()
    print('test ' + random.random()*100)
    sys.stdout.flush()
