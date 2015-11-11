# main.py
#
# Usage: main.py count interval
# Example: main.py 100 10
#
# Writes the system time <count> times into stdout with an interval of
# <interval> seconds

import sys
import time
import datetime

count = int(sys.argv[1])
interval = int(sys.argv[2])

for i in range(1, count+1):
  time.sleep(interval)
  print('%s: %d/%d (%d)' % (datetime.datetime.now(), i, count, interval))